
import pytest # type: ignore
from datetime import datetime
from app.models.file import File
from app.services.file_service import FileService
from app.domain.exceptions import NotFoundError, IllegalOperationError


class TestFileServiceCreate:
    """Tests for FileService.create() method."""
    
    def test_create_file_with_all_fields(self, app):
        """Test creating a file with all fields provided."""
        with app.app_context():
            file = FileService.create(
                filename="document.pdf",
                size_bytes=512000,
                storage_path="application/pdf"
            )
            
            assert file.id is not None
            assert file.filename == "document.pdf"
            assert file.size_bytes == 512000
            assert file.storage_path == "application/pdf"
    
    def test_create_file_with_minimal_fields(self, app):
        """Test creating a file with only required field (filename)."""
        with app.app_context():
            file = FileService.create(filename="test.txt",
            storage_path="application/pdf")
            
            assert file.id is not None
            assert file.filename == "test.txt"
            assert file.size_bytes is None
            assert file.storage_path == "application/pdf"
    
    def test_create_file_without_filename_fails(self, app):
        """Test that creating a file without a filename raises an error."""
        with app.app_context():
            with pytest.raises(IllegalOperationError):
                FileService.create(size_bytes=1024)


class TestFileServiceRead:
    """Tests for FileService read methods."""
    
    def test_get_all_files_empty(self, app):
        """Test getting all files when the database is empty."""
        with app.app_context():
            files = FileService.get_all()
            assert files == []
    
    def test_get_all_files(self, app):
        """Test getting all files."""
        with app.app_context():
            file1 = FileService.create(filename="file1.txt", size_bytes=1024, storage_path="/uploads/file1.txt")
            file2 = FileService.create(filename="file2.pdf", size_bytes=2048, storage_path="/uploads/file2.pdf")
            
            files = FileService.get_all()
            
            assert len(files) == 2
            assert file1 in files
            assert file2 in files
    
    def test_get_all_files_as_dict(self, app):
        """Test getting all files as dictionaries."""
        with app.app_context():
            FileService.create(filename="dict.txt", size_bytes=512, storage_path="text/plain")
            
            files_dict = FileService.get_all_dict()
            
            assert len(files_dict) == 1
            assert files_dict[0]["filename"] == "dict.txt"
            assert files_dict[0]["size_bytes"] == 512
    
    def test_get_file_by_id(self, app):
        """Test getting a file by its ID."""
        with app.app_context():
            file = FileService.create(filename="get_by_id.txt", storage_path="/uploads/get_by_id.txt")
            
            retrieved = FileService.get_by_id(file.id)
            
            assert retrieved.id == file.id
            assert retrieved.filename == "get_by_id.txt"
    
    def test_get_file_by_nonexistent_id_raises_error(self, app):
        """Test that getting a nonexistent file raises NotFoundError."""
        with app.app_context():
            with pytest.raises(NotFoundError):
                FileService.get_by_id(9999)


class TestFileServiceUpdate:
    """Tests for FileService.update() method."""
    
    def test_update_file_filename(self, app):
        """Test updating a file's filename."""
        with app.app_context():
            file = FileService.create(filename="old_filename.txt", size_bytes=1024, storage_path="/uploads/old_filename.txt")
            
            updated = FileService.update(file.id, filename="new_filename.txt")
            
            assert updated.filename == "new_filename.txt"
            assert updated.size_bytes == 1024
    
    def test_update_file_multiple_fields(self, app):
        """Test updating multiple fields."""
        with app.app_context():
            file = FileService.create(filename="file.txt", size_bytes=512, storage_path="/uploads/file.txt")
            
            updated = FileService.update(
                file.id,
                filename="updated.pdf",
                size_bytes=2048,
                storage_path="application/pdf"
            )
            
            assert updated.filename == "updated.pdf"
            assert updated.size_bytes == 2048
            assert updated.storage_path == "application/pdf"
    
    def test_update_nonexistent_file_raises_error(self, app):
        """Test that updating a nonexistent file raises NotFoundError."""
        with app.app_context():
            with pytest.raises(NotFoundError):
                FileService.update(9999, filename="new.txt")


class TestFileServiceDelete:
    """Tests for FileService.delete() method."""
    
    def test_delete_file(self, app):
        """Test deleting a file."""
        with app.app_context():
            file = FileService.create(filename="delete_me.txt", storage_path="/uploads/delete_me.txt")
            file_id = file.id
            
            result = FileService.delete(file_id)
            
            assert result is True
            with pytest.raises(NotFoundError):
                FileService.get_by_id(file_id)
    
    def test_delete_nonexistent_file_raises_error(self, app):
        """Test that deleting a nonexistent file raises NotFoundError."""
        with app.app_context():
            with pytest.raises(NotFoundError):
                FileService.delete(9999)
    
    def test_delete_removes_from_database(self, app):
        """Test that deleting removes the file from the database."""
        with app.app_context():
            file1 = FileService.create(filename="file1.txt", storage_path="/uploads/file1.txt")
            file2 = FileService.create(filename="file2.txt", storage_path="/uploads/file2.txt")
            
            FileService.delete(file1.id)
            
            files = FileService.get_all()
            assert len(files) == 1
            assert files[0].id == file2.id


class TestFileServiceIntegration:
    """Integration tests for FileService."""
    
    def test_complete_crud_cycle(self, app):
        """Test a complete CRUD cycle."""
        with app.app_context():
            # Create
            file = FileService.create(filename="crud.txt", size_bytes=1024, storage_path="text/plain")
            file_id = file.id
            
            # Read
            retrieved = FileService.get_by_id(file_id)
            assert retrieved.filename == "crud.txt"
            
            # Update
            updated = FileService.update(file_id, filename="updated.txt", size_bytes=2048)
            assert updated.filename == "updated.txt"
            assert updated.size_bytes == 2048
            
            # Verify update
            verified = FileService.get_by_id(file_id)
            assert verified.filename == "updated.txt"
            
            # Delete
            FileService.delete(file_id)
            with pytest.raises(NotFoundError):
                FileService.get_by_id(file_id)
    
    def test_multiple_files_lifecycle(self, app):
        """Test creating and managing multiple files."""
        with app.app_context():
            files = [
                FileService.create(filename=f"file{i}.txt", size_bytes=1024*i, storage_path=f"/uploads/file{i}.txt")
                for i in range(1, 4)
            ]
            
            assert len(FileService.get_all()) == 3
            
            FileService.delete(files[0].id)
            assert len(FileService.get_all()) == 2
            
            FileService.create(filename="file4.txt", size_bytes=4096, storage_path="/uploads/file4.txt")
            assert len(FileService.get_all()) == 3
