from app.models.base import db, TimestampMixin, BaseModel

class Simulator(db.Model, TimestampMixin, BaseModel):
    __tablename__ = 'simulators'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    from_file = db.Column(db.Boolean, nullable=False, default=True)
    simulator_url = db.Column(db.Text)

    specs_file_id = db.Column(db.Integer, db.ForeignKey('files.id'))
    specs_file = db.relationship("File")

    # Many-to-many: Data sources
    data_sources = db.relationship(
        "DataSource",
        secondary="simulator_data_sources",
        back_populates="simulators"
    )

    # Many-to-many: Roles
    roles = db.relationship(
        "Role",
        secondary="role_simulators",
        back_populates="simulators"
    )

    def __repr__(self):
        return f"<Simulator {self.title}>"
