from app.models.base import db, TimestampMixin, BaseModel

class DocumentPresentation(db.Model, TimestampMixin, BaseModel):
    __tablename__ = 'documents_presentations'

    id = db.Column(db.Integer, primary_key=True)
    main_title = db.Column(db.Text, nullable=False)
    auxiliary_title = db.Column(db.Text)
    description = db.Column(db.Text)

    file_id = db.Column(db.Integer, db.ForeignKey('files.id'))
    file = db.relationship("File")

    roles = db.relationship(
        "Role",
        secondary="role_documents_presentations",
        back_populates="documents_presentations"
    )

    def __repr__(self):
        return f"<DocumentPresentation {self.main_title}>"
