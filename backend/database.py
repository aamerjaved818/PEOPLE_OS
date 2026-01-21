from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from .config import settings

# Global engine cache (per environment URL)
_engine_cache = {}


def get_engine():
    """Get SQLAlchemy engine, dynamically resolved per environment.
    
    The engine is cached PER DATABASE URL, ensuring that different
    environments get separate engine instances.
    """
    db_url = settings.DATABASE_URL

    if db_url in _engine_cache:
        return _engine_cache[db_url]

    connect_args = {}
    pool_args = {}

    if "sqlite" in db_url:
        connect_args["check_same_thread"] = False
        if ":memory:" in db_url:
            pool_args["poolclass"] = StaticPool

    new_engine = create_engine(
        db_url,
        connect_args=connect_args,
        **pool_args
    )

    # Attach SQLite pragma for foreign keys
    if "sqlite" in db_url:
        @event.listens_for(new_engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    _engine_cache[db_url] = new_engine
    return new_engine


# Lazy engine property for backward compatibility
class _EngineProxy:
    """Lazy proxy that defers engine creation until first access."""
    _instance = None

    def __getattr__(self, name):
        if _EngineProxy._instance is None:
            _EngineProxy._instance = get_engine()
        return getattr(_EngineProxy._instance, name)


engine = _EngineProxy()

Base = declarative_base()


def get_session_local():
    """Get a sessionmaker bound to the current environment's engine."""
    return sessionmaker(autocommit=False, autoflush=False, bind=get_engine())


# Lazy SessionLocal for backward compatibility
class _SessionLocalProxy:
    """Lazy proxy that defers session creation until first access."""

    def __call__(self):
        return get_session_local()()


SessionLocal = _SessionLocalProxy()



