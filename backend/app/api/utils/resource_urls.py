import os
import shutil
import subprocess
import tempfile
import threading
import zipfile
from uuid import uuid4

from flask import current_app # type: ignore

from app.api.utils.check_roles import AccessChecker
from app.api.utils.file_utils import compute_sha256
from app.domain.exceptions import IllegalOperationError, NotFoundError
from app.models.data_source_file import DataSourceFile
from app.models.file import File
from app.services.data_source_service import DataSourceService
from app.services.file_service import FileService
from app.services.relations.simulator_data_source_relation import SimulatorDataSourceRelation
from app.services.relations.visor_data_source_relation import VisorDataSourceRelation


DATA_SOURCE_FILE_EXTENSIONS = {"csv", "xlsx", "parquet", "rdata", "rda", "rds"}

AUTO_DATA_SOURCE_DESCRIPTION = (
    "Fuente de datos generada automáticamente al cargar un proyecto Shiny. "
    "Por favor completa esta descripción con información relevante sobre su origen y contenido."
)

_DATA_SOURCE_RELATIONS = {
    "simulator": SimulatorDataSourceRelation,
    "visor": VisorDataSourceRelation,
}


def _link_data_source_to_resource(resource_type, resource_id, data_source_id):
    """Idempotently link a data source to the visor/simulator being processed."""
    relation = _DATA_SOURCE_RELATIONS.get(resource_type)
    if relation is None:
        return

    if relation.exists(resource_id, data_source_id):
        return

    if resource_type == "simulator":
        relation.add_data_source_to_simulator(resource_id, data_source_id)
    else:
        relation.add_data_source_to_visor(resource_id, data_source_id)


def _find_matching_data_source(file_type, checksum_sha256):
    """Find an existing data source whose exact (historic) file matches by format and checksum."""
    match = (
        DataSourceFile.query
        .join(DataSourceFile.file)
        .filter(File.file_type == file_type, File.checksum_sha256 == checksum_sha256)
        .first()
    )
    return match.data_source_id if match else None


def _register_new_data_source(file_path, filename, file_type):
    """Move a file into permanent storage and create a data source from it."""
    storage_root = current_app.config["FILE_STORAGE_ROOT"]
    os.makedirs(storage_root, exist_ok=True)

    storage_path = os.path.join(storage_root, f"{uuid4()}.{file_type}")
    shutil.move(file_path, storage_path)

    file_record = FileService.create(
        filename=filename,
        storage_path=storage_path,
        file_type=file_type,
        size_bytes=os.path.getsize(storage_path),
        checksum_sha256=compute_sha256(storage_path),
    )

    data_source = DataSourceService.create(
        name=filename[:120],
        description=AUTO_DATA_SOURCE_DESCRIPTION,
        file_id=file_record.id,
    )
    AccessChecker.grant_admin_access(data_source.id, "data_source")

    return data_source.id


def _extract_data_sources_from_app(target_folder, resource_id, resource_type):
    """Replace known data-file formats found in a Shiny app folder with data sources.

    Walks the app folder looking for csv/xlsx/parquet/RData/rda/rds files. Each one
    is deduplicated against existing data sources by (format, sha256): if a match is
    found, the copy inside the app folder is replaced with a symlink to that data
    source's current version instead of keeping a redundant copy; otherwise a new
    data source is created from it. Either way, the app folder ends up with a
    symlink at the exact same relative path the file had, so the Shiny app itself
    runs unmodified, and the resulting data source is linked to the visor/simulator
    being processed.
    """
    for dirpath, _dirnames, filenames in os.walk(target_folder):
        for filename in filenames:
            file_type = os.path.splitext(filename)[1].lstrip(".").lower()
            if file_type not in DATA_SOURCE_FILE_EXTENSIONS:
                continue

            file_path = os.path.join(dirpath, filename)
            if os.path.islink(file_path):
                continue

            checksum = compute_sha256(file_path)
            data_source_id = _find_matching_data_source(file_type, checksum)

            if data_source_id is not None:
                os.remove(file_path)
            else:
                data_source_id = _register_new_data_source(file_path, filename, file_type)

            current_symlink_path = DataSourceService.get_by_id(data_source_id).file.storage_path
            os.symlink(current_symlink_path, file_path)

            _link_data_source_to_resource(resource_type, resource_id, data_source_id)


def _run_restore_app_async(resource_id: str, resource_type: str) -> None:
    """Run the restore_app.sh script asynchronously in a background thread.
    
    Args:
        resource_id: The unique identifier for the resource
        resource_type: The type of resource (e.g., 'simulator', 'visor')
    """
    # Capture the app object while in the application context
    app = current_app._get_current_object()
    
    def run_restore():
        # Create an application context for the background thread
        with app.app_context():
            try:
                # Construct the container name based on environment
                container_name = app.config.get('SHINY_CONTAINER_NAME', 'app_shiny_dev')
                
                # Run the restore_app.sh script inside the container
                cmd = [
                    'docker', 'exec', container_name,
                    'bash', 'scripts/restore_app.sh', str(resource_type), str(resource_id)
                ]
                
                result = subprocess.run(
                    cmd,
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=1800  # 30 minute timeout for background tasks
                )
                
                app.logger.info(
                    f"restore_app.sh executed for {resource_type}/{resource_id}: {result.stdout}"
                )
            except subprocess.TimeoutExpired:
                app.logger.error(
                    f"restore_app.sh timeout for {resource_type}/{resource_id}: "
                    f"Processing took longer than 30 minutes"
                )
            except subprocess.CalledProcessError as e:
                app.logger.error(
                    f"restore_app.sh failed for {resource_type}/{resource_id}: {e.stderr}"
                )
            except Exception as e:
                app.logger.error(
                    f"Unexpected error running restore_app.sh for {resource_type}/{resource_id}: {str(e)}"
                )
    
    # Start the restore script in a background thread
    thread = threading.Thread(
        target=run_restore,
        daemon=True,
        name=f"restore_app_{resource_type}_{resource_id}"
    )
    thread.start()


def build_resource_url(file, resource_id, type) -> str:
    """Build a resource URL by processing an uploaded zip file.
    
    This function:
    1. Extracts the zip file to a temporary directory
    2. Validates that the extracted content has required files (renv.lock and app.R)
    3. Moves the unzipped content to the shared resources folder
    4. Replaces any csv/xlsx/parquet/RData/rda/rds file found in the app with a
       data source (reusing an existing one if its checksum already matches),
       symlinked back at its original path and linked to this resource
    5. Runs the restore_app.sh script in the shiny-server container
    6. Returns the resource URL
    
    Args:
        file: The uploaded zip file object
        resource_id: The unique identifier for the resource
        type: The type of resource (e.g., 'simulator', 'visor')
        
    Returns:
        str: The URL to access the resource
        
    Raises:
        IllegalOperationError: If the zip file doesn't contain required files
    """
    # Create a temporary directory to extract the zip file
    with tempfile.TemporaryDirectory() as temp_dir:
        # Extract the zip file
        zip_path = os.path.join(temp_dir, "app.zip")
        file.save(zip_path)
        
        extract_dir = os.path.join(temp_dir, "extracted")
        os.makedirs(extract_dir)
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
        except zipfile.BadZipFile:
            raise IllegalOperationError("El archivo no es un ZIP válido")
        
        # Check for required files (renv.lock)
        required_files = ['renv.lock']
        found_files = []
        
        for root, dirs, files in os.walk(extract_dir):
            found_files.extend(files)
        
        missing_files = [f for f in required_files if f not in found_files]
        if missing_files:
            raise IllegalOperationError(
                f"El archivo ZIP debe contener los archivos: {', '.join(required_files)}. "
                f"Archivos faltantes: {', '.join(missing_files)}"
            )
        
        # Create the target folder in the shared resources directory
        target_folder = f"{current_app.config['RESOURCES_SHARED_FOLDER']}/{type}/{resource_id}"
        os.makedirs(target_folder, exist_ok=True)
        
        # Move the extracted content to the target folder
        # First, remove any existing content in the target folder
        shutil.rmtree(target_folder)
        os.makedirs(target_folder)
        
        # Move only the contents of the extracted archive, not the wrapper folder itself.
        for item in os.listdir(extract_dir):
            src = os.path.join(extract_dir, item)
            if os.path.isdir(src):
                for nested_item in os.listdir(src):
                    nested_src = os.path.join(src, nested_item)
                    nested_dst = os.path.join(target_folder, nested_item)
                    shutil.move(nested_src, nested_dst)
            else:
                shutil.move(src, os.path.join(target_folder, item))

        # Replace known data-file formats with data sources (deduplicated by
        # checksum) linked to this resource, symlinking them back in place.
        _extract_data_sources_from_app(target_folder, resource_id, type)

        # Run the restore_app.sh script asynchronously in the background
        _run_restore_app_async(resource_id, type)
        
    return os.path.join(current_app.config['RESOURCES_BASE_URL'], type, str(resource_id),'')


def delete_resource_file(resource_id, type) -> None:
    """Delete a resource file and its contents from the shared resources folder.
    
    Args:
        resource_id: The unique identifier for the resource
        type: The type of resource (e.g., 'simulator', 'visor')
        
    Raises:
        NotFoundError: If the resource doesn't exist in the shared resources folder
    """
    target_folder = f"{current_app.config['RESOURCES_SHARED_FOLDER']}/{type}/{resource_id}"
    
    # Check that the resource exists
    if not os.path.exists(target_folder):
        raise NotFoundError(
            f"No se encontró el recurso con ID {resource_id} de tipo {type}"
        )
    
    # Delete the resource folder and all its content
    try:
        shutil.rmtree(target_folder)
    except Exception as e:
        current_app.logger.error(f"Error deleting resource folder {target_folder}: {str(e)}")
        raise NotFoundError(
            f"Error al eliminar el recurso: {str(e)}"
        )
