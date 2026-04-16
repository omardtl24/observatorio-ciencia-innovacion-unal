from app.models.base import db, TimestampMixin, BaseModel


class Role(db.Model, TimestampMixin, BaseModel):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)

    users = db.relationship(
        "User",
        secondary="user_roles",
        back_populates="roles"
    )

    reports = db.relationship("Report",
                              secondary="role_reports",
                              back_populates="roles")
    visors = db.relationship("Visor",
                             secondary="role_visors",
                             back_populates="roles")
    simulators = db.relationship("Simulator",
                                 secondary="role_simulators",
                                 back_populates="roles")

    data_sources = db.relationship("DataSource",
                                   secondary="role_data_sources",
                                   back_populates="roles")
                                 
    documents_presentations = db.relationship(
        "DocumentPresentation",
        secondary="role_documents_presentations",
        back_populates="roles"
    )

    def __repr__(self):
        return f"<Role {self.name}>"
