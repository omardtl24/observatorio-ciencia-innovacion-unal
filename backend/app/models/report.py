from app.models.base import db, TimestampMixin, BaseModel

class Report(db.Model, TimestampMixin, BaseModel):
    __tablename__ = 'reports'

    id = db.Column(db.Integer, primary_key=True)
    main_title = db.Column(db.Text, nullable=False)
    auxiliary_title = db.Column(db.Text)
    description = db.Column(db.Text)

    document_file_id = db.Column(db.Integer, db.ForeignKey('files.id'))
    document_file = db.relationship("File")

    data_sources = db.relationship(
        "DataSource",
        secondary="report_data_sources",
        back_populates="reports"
    )

    roles = db.relationship(
        "Role",
        secondary="role_reports",
        back_populates="reports"
    )

    def __repr__(self):
        return f"<Report {self.main_title}>"