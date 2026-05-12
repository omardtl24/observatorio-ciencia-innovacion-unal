import os
import shutil
import subprocess
import tempfile
import threading
import zipfile

from flask import current_app # type: ignore

from app.domain.exceptions import IllegalOperationError, NotFoundError


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
    4. Runs the restore_app.sh script in the shiny-server container
    5. Returns the resource URL
    
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
