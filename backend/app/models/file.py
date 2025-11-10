from app.models.base import db, BaseModel

class File(db.Model, BaseModel):
    __tablename__ = 'files'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.Text, nullable=False)
    storage_path = db.Column(db.Text, nullable=False)
    file_type = db.Column(db.Text)
    size_bytes = db.Column(db.BigInteger)
    checksum_sha256 = db.Column(db.Text)
    uploaded_at = db.Column(db.DateTime, default=db.func.now())

    def __repr__(self):
        return f"<File {self.filename}>"