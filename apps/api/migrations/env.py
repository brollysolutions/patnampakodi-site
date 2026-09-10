from alembic import context
from sqlalchemy import create_engine

from app.db import migration_url

engine = create_engine(
    migration_url().replace("postgresql://", "postgresql+psycopg://", 1),
    connect_args={"connect_timeout": 3},
)
with engine.connect() as connection:
    context.configure(connection=connection)
    with context.begin_transaction():
        context.run_migrations()
