from app.models.base import db
from app.models.role import Role
from app.models.user import User
from app.models.file import File
from app.models.simulator import Simulator
from app.models.visor import Visor
from app.models.report import Report
from app.models.data_source import DataSource
from app.models.documents_presentation import DocumentPresentation
from app.models.relations import (
    report_data_sources,
    visor_data_sources,
    simulator_data_sources,
    role_reports,
    role_visors,
    role_simulators,
    role_data_sources,
)
