from src.core.config import settings
from src.db.session import engine
from src.db.base import Base

def init_db():
    # metadata to‘lishi uchun import
    from src.models import user  # noqa
    from src.models import transaction  # noqa
    from src.models import audit_log  # noqa

    if settings.AUTO_CREATE_TABLES:
        Base.metadata.create_all(bind=engine)
