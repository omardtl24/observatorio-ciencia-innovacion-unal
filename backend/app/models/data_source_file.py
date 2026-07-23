from app.models.base import db, BaseModel

class DataSourceFile(db.Model, BaseModel):
    """Historic record of every file ever published under a data source."""
    __tablename__ = 'data_source_files'

    id = db.Column(db.Integer, primary_key=True)
    data_source_id = db.Column(db.Integer, db.ForeignKey('data_sources.id', ondelete='CASCADE'), nullable=False)
    file_id = db.Column(db.Integer, db.ForeignKey('files.id', ondelete='RESTRICT'), nullable=False)
    published_at = db.Column(db.DateTime, default=db.func.now(), nullable=False)

    data_source = db.relationship("DataSource", back_populates="file_versions")
    file = db.relationship("File")

    __table_args__ = (
        db.UniqueConstraint('data_source_id', 'file_id', name='uq_data_source_file'),
    )

    def __repr__(self):
        return f"<DataSourceFile data_source_id={self.data_source_id} file_id={self.file_id}>"
