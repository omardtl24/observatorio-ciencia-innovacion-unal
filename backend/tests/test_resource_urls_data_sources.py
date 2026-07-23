"""Tests for the automatic data-source extraction in app.api.utils.resource_urls."""

import io
import os
import zipfile

import pytest # type: ignore

from app.api.utils import resource_urls
from app.services.data_source_service import DataSourceService
from app.services.file_service import FileService
from app.services.role_service import RoleService
from app.services.simulator_service import SimulatorService
from app.services.relations.simulator_data_source_relation import SimulatorDataSourceRelation


@pytest.fixture(autouse=True)
def _isolated_storage(app, tmp_path):
    app.config["FILE_STORAGE_ROOT"] = str(tmp_path / "storage")
    app.config["RESOURCES_SHARED_FOLDER"] = str(tmp_path / "shiny-apps")
    os.makedirs(app.config["FILE_STORAGE_ROOT"], exist_ok=True)
    yield


@pytest.fixture(autouse=True)
def _admin_role(app, reset_database):
    # grant_admin_access requires a real "Administrador" role to exist.
    with app.app_context():
        RoleService.create(name="Administrador", description="Admin role for tests")
    yield


@pytest.fixture
def simulator(app):
    with app.app_context():
        yield SimulatorService.create(title="Test simulator", from_file=True)


def _write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(content)
    return path


class TestExtractDataSourcesFromApp:
    def test_creates_new_data_source_and_symlinks_in_place(self, app, tmp_path, simulator):
        with app.app_context():
            target_folder = str(tmp_path / "app1")
            csv_path = _write_file(os.path.join(target_folder, "data.csv"), b"a,b\n1,2\n")

            resource_urls._extract_data_sources_from_app(target_folder, simulator.id, "simulator")

            assert os.path.islink(csv_path)

            with open(csv_path, "rb") as f:
                assert f.read() == b"a,b\n1,2\n"

            data_sources = DataSourceService.get_all()
            assert len(data_sources) == 1
            assert data_sources[0].name == "data.csv"
            assert "automáticamente" in data_sources[0].description

            assert SimulatorDataSourceRelation.exists(simulator.id, data_sources[0].id)

    def test_reuses_existing_data_source_with_matching_checksum(self, app, tmp_path, simulator):
        with app.app_context():
            existing_file = FileService.create(
                filename="prior.csv",
                storage_path=str(_write_file(tmp_path / "prior_storage" / "prior.csv", b"same,content\n")),
                file_type="csv",
                size_bytes=13,
                checksum_sha256=resource_urls.compute_sha256(str(tmp_path / "prior_storage" / "prior.csv")),
            )
            existing_data_source = DataSourceService.create(
                name="Prior source", description="desc", file_id=existing_file.id
            )

            target_folder = str(tmp_path / "app2")
            csv_path = _write_file(os.path.join(target_folder, "renamed.csv"), b"same,content\n")

            resource_urls._extract_data_sources_from_app(target_folder, simulator.id, "simulator")

            assert len(DataSourceService.get_all()) == 1

            expected_target = DataSourceService.get_by_id(existing_data_source.id).file.storage_path
            assert os.readlink(csv_path) == expected_target
            assert SimulatorDataSourceRelation.exists(simulator.id, existing_data_source.id)

    def test_ignores_non_data_extensions(self, app, tmp_path, simulator):
        with app.app_context():
            target_folder = str(tmp_path / "app3")
            app_r_path = _write_file(os.path.join(target_folder, "app.R"), b"shinyApp(...)")
            lock_path = _write_file(os.path.join(target_folder, "renv.lock"), b"{}")

            resource_urls._extract_data_sources_from_app(target_folder, simulator.id, "simulator")

            assert DataSourceService.get_all() == []
            assert not os.path.islink(app_r_path)
            assert not os.path.islink(lock_path)

    def test_deduplicates_identical_files_within_same_run(self, app, tmp_path, simulator):
        with app.app_context():
            target_folder = str(tmp_path / "app4")
            path_a = _write_file(os.path.join(target_folder, "a.csv"), b"dup,content\n")
            path_b = _write_file(os.path.join(target_folder, "nested", "b.csv"), b"dup,content\n")

            resource_urls._extract_data_sources_from_app(target_folder, simulator.id, "simulator")

            assert len(DataSourceService.get_all()) == 1
            assert os.readlink(path_a) == os.readlink(path_b)

    def test_second_run_for_same_resource_does_not_duplicate_link(self, app, tmp_path, simulator):
        with app.app_context():
            target_folder = str(tmp_path / "app5")
            csv_path = _write_file(os.path.join(target_folder, "data.csv"), b"x,y\n1,2\n")

            resource_urls._extract_data_sources_from_app(target_folder, simulator.id, "simulator")
            data_source_id = DataSourceService.get_all()[0].id

            # Simulate a redeploy: the app folder is recreated with the same file.
            target_folder_2 = str(tmp_path / "app5-redux")
            csv_path_2 = _write_file(os.path.join(target_folder_2, "data.csv"), b"x,y\n1,2\n")
            resource_urls._extract_data_sources_from_app(target_folder_2, simulator.id, "simulator")

            assert len(DataSourceService.get_all()) == 1
            assert os.readlink(csv_path_2) == os.readlink(csv_path)


class TestBuildResourceUrlEndToEnd:
    def _make_zip_bytes(self, files):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as zf:
            for name, content in files.items():
                zf.writestr(name, content)
        buffer.seek(0)
        return buffer

    def test_build_resource_url_extracts_and_links_data_source(self, app, monkeypatch, simulator):
        monkeypatch.setattr(resource_urls, "_run_restore_app_async", lambda *a, **k: None)

        zip_bytes = self._make_zip_bytes({
            "myapp/renv.lock": b"{}",
            "myapp/app.R": b"shinyApp(...)",
            "myapp/data/sales.csv": b"date,amount\n2024-01-01,100\n",
        })

        class FakeUpload:
            def save(self, path):
                with open(path, "wb") as f:
                    f.write(zip_bytes.read())

        with app.app_context():
            resource_urls.build_resource_url(FakeUpload(), simulator.id, "simulator")

            target_folder = f"{app.config['RESOURCES_SHARED_FOLDER']}/simulator/{simulator.id}"
            csv_path = os.path.join(target_folder, "data", "sales.csv")

            assert os.path.islink(csv_path)
            with open(csv_path, "rb") as f:
                assert f.read() == b"date,amount\n2024-01-01,100\n"

            data_sources = DataSourceService.get_all()
            assert len(data_sources) == 1
            assert data_sources[0].name == "sales.csv"
            assert SimulatorDataSourceRelation.exists(simulator.id, data_sources[0].id)
