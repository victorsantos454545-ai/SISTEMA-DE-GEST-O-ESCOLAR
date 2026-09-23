from datetime import datetime, timezone
from app.extensions import db


class TimestampMixin:
    """Mixin que adiciona campos created_at e updated_at aos modelos."""
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
