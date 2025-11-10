from app.services.base_service import BaseService
from app.models.report import Report

class ReportService(BaseService):
    model = Report
