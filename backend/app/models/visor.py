from app.models.base import db, TimestampMixin, BaseModel

class Visor(db.Model, TimestampMixin, BaseModel):
    __tablename__ = 'visors'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    from_file = db.Column(db.Boolean, nullable=False, default=True)
    visor_url = db.Column(db.Text)

    data_sources = db.relationship(
        "DataSource",
        secondary="visor_data_sources",
        back_populates="visors"
    )

    roles = db.relationship(
        "Role",
        secondary="role_visors",
        back_populates="visors"
    )

    def __repr__(self):
        return f"<Visor {self.title}>"
