from app.models.base import db, TimestampMixin, BaseModel

class User(db.Model, TimestampMixin, BaseModel):
    __tablename__ = 'users'

    email = db.Column(db.String(120), primary_key=True)
    names = db.Column(db.String(120), nullable=False)
    last_names = db.Column(db.String(120), nullable=False)
    last_login_at = db.Column(db.DateTime)

    roles = db.relationship(
        "Role",
        secondary="user_roles",
        back_populates="users",
        lazy='joined'
    )

    def __repr__(self):
        return f"<User {self.email}>"
