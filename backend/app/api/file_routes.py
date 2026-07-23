import os
from datetime import datetime
from uuid import uuid4
from flask import Blueprint, jsonify, current_app, send_file, request # type: ignore
from werkzeug.utils import secure_filename # type: ignore
from flask_jwt_extended import jwt_required, get_jwt_identity # type: ignore
from app.services.file_garbage_collector_service import FileGarbageCollectorService
from app.services.file_service import FileService
from app.domain.exceptions import IllegalOperationError, SchemaValidationError, UnauthorizedError
from app.api.utils.check_roles import AccessChecker, assert_admin
from app.api.utils.file_utils import compute_sha256, validate_sha256

file_bp = Blueprint("file", __name__, url_prefix="/file")

@file_bp.post("/upload")
@jwt_required()
def upload():
    """Upload a new file to the system.
    
    Expects a multipart/form-data request with a 'file' field.
    The file is stored on disk with a unique UUID-based name and
    metadata is saved to the database including SHA256 checksum.
    
    Form Data:
        file (file, required): The file to upload.
    
    Returns:
        dict: The created file record with id, filename, file_type, and size_bytes (status 201).
    
    Raises:
        400: If file is missing or filename is empty.
        401: If not authenticated (when JWT is enabled).
    """

    assert_admin("El usuario no tiene permiso para cargar archivos")

    if "file" not in request.files:
        raise SchemaValidationError("Debes adjuntar un archivo")

    uploaded = request.files["file"]

    if uploaded.filename == "":
        raise SchemaValidationError("El nombre del archivo es requerido")

    original_filename = secure_filename(uploaded.filename)
    file_type = os.path.splitext(original_filename)[1].lower().lstrip(".")

    storage_root = current_app.config.get("FILE_STORAGE_ROOT")
    os.makedirs(storage_root, exist_ok=True)

    storage_name = f"{uuid4()}.{file_type}" if file_type else str(uuid4())
    storage_path = os.path.join(storage_root, storage_name)

    uploaded.save(storage_path)

    size_bytes = os.path.getsize(storage_path)
    checksum_sha256 = compute_sha256(storage_path)

    file_data = {
        "filename": original_filename,
        "storage_path": storage_path,
        "file_type": file_type,
        "size_bytes": size_bytes,
        "checksum_sha256": checksum_sha256,
    }

    file_record = FileService.create(**file_data)

    return jsonify(file_record.to_dict(include=["id", "filename", "file_type", "size_bytes"])), 201



@file_bp.put("/update/<file_id>")
@jwt_required()
def update(file_id):
    """Update an existing file by replacing it with a new one.
    
    The old file is deleted from disk after successful update.
    Expects a multipart/form-data request with a 'file' field.
    
    Path Parameters:
        file_id (str): The ID of the file to update.
    
    Form Data:
        file (file, required): The new file to upload.
    
    Returns:
        dict: The updated file record with id, filename, file_type, and size_bytes (status 200).
    
    Raises:
        400: If file is missing or filename is empty.
        401: If not authenticated (when JWT is enabled).
        404: If file_id does not exist.
    """

    assert_admin("El usuario no tiene permiso para actualizar archivos")

    if "file" not in request.files:
        raise SchemaValidationError("El archivo es requerido")

    uploaded = request.files["file"]

    if uploaded.filename == "":
        raise SchemaValidationError("El nombre del archivo es requerido")

    file = FileService.get_by_id(file_id)

    old_path = file.storage_path

    original_filename = secure_filename(uploaded.filename)
    file_type = os.path.splitext(original_filename)[1].lower().lstrip(".")

    storage_root = current_app.config.get("FILE_STORAGE_ROOT")
    os.makedirs(storage_root, exist_ok=True)

    storage_name = f"{uuid4()}.{file_type}" if file_type else str(uuid4())
    new_storage_path = os.path.join(storage_root, storage_name)

    uploaded.save(new_storage_path)

    size_bytes = os.path.getsize(new_storage_path)
    checksum_sha256 = compute_sha256(new_storage_path)

    update_data = {
        "filename": original_filename,
        "storage_path": new_storage_path,
        "file_type": file_type,
        "size_bytes": size_bytes,
        "checksum_sha256": checksum_sha256,
    }

    file_record = FileService.update(file_id, **update_data)

    if os.path.exists(old_path):
        os.remove(old_path)

    return jsonify(file_record.to_dict(include=["id",
                                                "filename",
                                                "file_type",
                                                "size_bytes"])), 200

    

@file_bp.get("/download/<file_id>")
@jwt_required()
def download(file_id):
    """Download a file or display it in the browser.
    
    Validates file integrity using SHA256 checksum before serving.
    Requires query parameters to validate access to the associated resource.
    
    Path Parameters:
        file_id (str): The ID of the file to download.
    
    Query Parameters:
        resource (str, required): The type of resource (e.g., 'visor', 'report').
        id (str, required): The ID of the resource that owns this file.
        display (str, required): 'true' to display in browser, 'false' to download.
    
    Returns:
        file: The file content with appropriate headers.
    
    Raises:
        400: If required query parameters are missing.
        401: If not authenticated (when JWT is enabled).
        404: If file_id does not exist.
        500: If file integrity check fails (checksum mismatch).
    """
    resource_origin = request.args.get("resource")
    resource_id = request.args.get("id")
    display = request.args.get("display", "false").lower() == "true"
    if not resource_origin or not resource_id or not display:
        raise IllegalOperationError("Faltan parámetros de consulta: resource, id y display son requeridos")
    
    user_email = get_jwt_identity()
    if not AccessChecker.check_access(user_email, resource_id, resource_origin):
        raise UnauthorizedError("El usuario no tiene permiso para acceder a este recurso")
    
    file = FileService.get_by_id(file_id)
    file_path = file.storage_path

    if not validate_sha256(file.storage_path, file.checksum_sha256):
        raise IllegalOperationError(
            "Error en la verificación de integridad del archivo (suma de comprobación no coincide)"
        )

    return send_file(file_path, as_attachment=not display)

@file_bp.get("/metadata/<file_id>")
@jwt_required()
def metadata(file_id):
    """Get metadata for a specific file.
    
    Returns basic information about the file without downloading it.
    
    Path Parameters:
        file_id (str): The ID of the file.
    
    Returns:
        dict: File metadata including id, filename, file_type, and size_bytes (status 200).
    
    Raises:
        401: If not authenticated (when JWT is enabled).
        404: If file_id does not exist.
    """
    
    assert_admin("El usuario no tiene permiso para ver los metadatos del archivo")

    file = FileService.get_by_id(file_id)

    return jsonify(file.to_dict(include=["id", "filename", "file_type", "size_bytes"])), 200

@file_bp.get("/all")
@jwt_required()
def all_files():
    """Retrieve all files in the system.
    
    Returns basic metadata for all files stored in the system.
    
    Returns:
        list: A list of file records with id, filename, file_type, and size_bytes (status 200).
    
    Raises:
        401: If not authenticated (when JWT is enabled).
    """

    assert_admin("El usuario no tiene permiso para ver todos los archivos")

    files = FileService.get_all_dict(include=["id",
                                              "filename", 
                                              "file_type", 
                                              "size_bytes"])
    
    return jsonify(files), 200

@file_bp.delete("/<file_id>")
@jwt_required()
def delete(file_id):
    """Delete a file from the system.
    
    Removes both the database record and the physical file from storage.
    
    Path Parameters:
        file_id (str): The ID of the file to delete.
    
    Returns:
        Empty response with status 204 (No Content).
    
    Raises:
        401: If not authenticated (when JWT is enabled).
        404: If file_id does not exist.
    """

    assert_admin("El usuario no tiene permiso para eliminar archivos")

    file = FileService.get_by_id(file_id)
    storage_path = file.storage_path
    FileService.delete(file_id)

    if os.path.exists(storage_path):
        os.remove(storage_path)

    return "", 204


@file_bp.get("/orphaned")
@jwt_required()
def preview_orphaned_files():
    """List files that would be removed by POST /file/gc, without deleting anything.

    Covers both kinds of orphan: File records not linked to any entity, and
    files sitting directly under FILE_STORAGE_ROOT (not in subfolders) with no
    File record at all.

    The grace period only applies to the automated background sweep, which
    can't tell an orphan from a file mid-upload. A human explicitly asking to
    preview/run this gets an immediate answer instead - no grace period by
    default. Pass grace_period_seconds to opt into one anyway.

    Query Parameters:
        grace_period_seconds (int, optional): Minimum age, in seconds, below
            which an unlinked/untracked file is excluded from the results.
            Defaults to 0 (no grace period) for this manually-triggered route.

    Returns:
        dict: {
            "orphaned_file_records": [{id, filename, file_type, size_bytes, uploaded_at}, ...],
            "untracked_disk_files": [{path, size_bytes, modified_at}, ...],
        } (status 200).

    Raises:
        401: If not authenticated (when JWT is enabled).
        400: If the user is not an administrator.
    """

    assert_admin("El usuario no tiene permiso para ver los archivos huérfanos")

    grace_period_seconds = request.args.get("grace_period_seconds", default=0, type=int)

    orphaned = FileGarbageCollectorService.find_orphaned_files(grace_period_seconds=grace_period_seconds)
    untracked = FileGarbageCollectorService.find_untracked_disk_files(grace_period_seconds=grace_period_seconds)

    payload = {
        "orphaned_file_records": [
            {
                **file.to_dict(include=["id", "filename", "file_type", "size_bytes"]),
                "uploaded_at": file.uploaded_at.isoformat() if file.uploaded_at else None,
            }
            for file in orphaned
        ],
        "untracked_disk_files": [
            {
                "path": path,
                "size_bytes": os.path.getsize(path) if os.path.exists(path) else None,
                "modified_at": datetime.fromtimestamp(os.lstat(path).st_mtime).isoformat(),
            }
            for path in untracked
        ],
    }

    return jsonify(payload), 200


@file_bp.post("/gc")
@jwt_required()
def collect_orphaned_files():
    """Trigger the orphaned-files garbage collector.

    Deletes files (database record and on-disk content) that are not linked
    to any report, simulator, document/presentation, or data source - as well
    as any files sitting directly under FILE_STORAGE_ROOT (not in subfolders)
    with no File record at all. Uses the same underlying cleanup as the
    `flask cleanup-orphaned-files` CLI command and the background daemon.

    Unlike the background daemon, this is a human explicitly asking for
    cleanup right now, so it does not wait out the configured grace period by
    default - any orphan, however recent, is removed. Pass
    grace_period_seconds to keep a safety margin instead.

    Query Parameters:
        grace_period_seconds (int, optional): Minimum age, in seconds, an
            unlinked/untracked file must have before this route will remove
            it. Defaults to 0 (no grace period) for this manually-triggered route.

    Returns:
        dict: {"orphaned_file_records": int, "untracked_disk_files": int, "removed": int}
            with status 200.

    Raises:
        401: If not authenticated (when JWT is enabled).
        400: If the user is not an administrator.
    """

    assert_admin("El usuario no tiene permiso para ejecutar la limpieza de archivos huérfanos")

    grace_period_seconds = request.args.get("grace_period_seconds", default=0, type=int)

    result = FileGarbageCollectorService.collect(
        grace_period_seconds=grace_period_seconds, logger=current_app.logger
    )

    return jsonify(result), 200
