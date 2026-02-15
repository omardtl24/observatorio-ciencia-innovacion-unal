
import pytest
import os
from flask import Flask
from app.models.base import db
from app import create_app
from app.services.file_service import FileService
from app.services.role_service import RoleService


@pytest.fixture(scope="session")
def app():
    """Create and configure a Flask app for testing."""
    os.environ["TESTING"] = "True"
    app = create_app(config_name="testing")
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's CLI commands."""
    return app.test_cli_runner()


@pytest.fixture(autouse=True)
def reset_database(app):
    """Reset database before each test."""
    with app.app_context():
        db.session.rollback()
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()
        yield
        db.session.rollback()


@pytest.fixture
def test_file(app):
    """Create a test file that can be used for DataSource tests."""
    with app.app_context():
        file = FileService.create(filename="test_file.txt",
                                  storage_path="text/plain")
        yield file


@pytest.fixture
def test_role(app):
    """Create a test role that can be used for relationship tests."""
    with app.app_context():
        role = RoleService.create(name="Test Role", description="Test role for testing")
        yield role

