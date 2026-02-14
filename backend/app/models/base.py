from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BaseModel:
    """Provides reusable db helper methods for all models."""

    @classmethod
    def create(cls, **kwargs):
        """Create a new record and commit it."""
        instance = cls(**kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance

    def save(self):
        """Commit changes already applied to this object."""
        db.session.commit()
        return self

    def update(self, **kwargs):
        """Update fields and save."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self.save()

    def delete(self):
        """Delete the record from the DB."""
        db.session.delete(self)
        db.session.commit()
    

    def to_dict(self, include=None, exclude=None):
        columns = [c.name for c in self.__table__.columns]
        if include:
            columns = [col for col in columns if col in include]
        if exclude:
            columns = [col for col in columns if col not in exclude]
        return {col: getattr(self, col) for col in columns}

