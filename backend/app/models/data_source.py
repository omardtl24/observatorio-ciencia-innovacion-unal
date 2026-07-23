from app.models.base import db, TimestampMixin, BaseModel

class DataSource(db.Model, TimestampMixin, BaseModel):
    __tablename__ = 'data_sources'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)

    file_id = db.Column(db.Integer, db.ForeignKey('files.id'), nullable=False)
    file = db.relationship("File")

    file_versions = db.relationship(
        "DataSourceFile",
        back_populates="data_source",
        order_by="DataSourceFile.published_at.desc()",
        cascade="all, delete-orphan"
    )

    reports = db.relationship(
        "Report",
        secondary="report_data_sources",
        back_populates="data_sources"
    )

    visors = db.relationship(
        "Visor",
        secondary="visor_data_sources",
        back_populates="data_sources"
    )

    simulators = db.relationship(
        "Simulator",
        secondary="simulator_data_sources",
        back_populates="data_sources"
    )

    roles = db.relationship(
        "Role",
        secondary="role_data_sources",
        back_populates="data_sources"
    )

    def __repr__(self):
        return f"<DataSource {self.name}>"
