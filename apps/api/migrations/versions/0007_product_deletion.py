"""Allow brand-scoped deletion of unused variants; preserve other table grants."""

from alembic import op

revision = "0007_product_deletion"
down_revision = "0006_instant_checkout"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("GRANT DELETE ON variants TO pakodi_app")


def downgrade():
    op.execute("REVOKE DELETE ON variants FROM pakodi_app")
