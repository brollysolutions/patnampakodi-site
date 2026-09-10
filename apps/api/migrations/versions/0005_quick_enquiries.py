"""Retry-safe phone-first enquiries; existing full enquiries remain valid."""

from alembic import op

revision = "0005_quick_enquiries"
down_revision = "0004_operations"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TABLE enquiries ADD COLUMN request_key uuid, ADD COLUMN request_hash text")
    op.execute(
        "CREATE UNIQUE INDEX enquiry_request_key ON enquiries(brand_id, request_key) "
        "WHERE request_key IS NOT NULL"
    )


def downgrade():
    op.execute("DROP INDEX enquiry_request_key")
    op.execute("ALTER TABLE enquiries DROP COLUMN request_key, DROP COLUMN request_hash")
