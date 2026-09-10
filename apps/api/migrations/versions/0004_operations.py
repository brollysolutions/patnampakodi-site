"""Durable job health for the operator dashboard."""

from alembic import op

revision = "0004_operations"
down_revision = "0003_payment_ownership"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
      CREATE TABLE operation_checks (
        brand_id text NOT NULL, name text NOT NULL, status text NOT NULL,
        checked_at timestamptz NOT NULL DEFAULT now(), PRIMARY KEY(brand_id,name));
      ALTER TABLE operation_checks ENABLE ROW LEVEL SECURITY;
      ALTER TABLE operation_checks FORCE ROW LEVEL SECURITY;
      CREATE POLICY brand_scope ON operation_checks TO pakodi_app
        USING(brand_id=current_setting('app.brand_id',true))
        WITH CHECK(brand_id=current_setting('app.brand_id',true));
      REVOKE ALL ON operation_checks FROM PUBLIC;
      GRANT SELECT,INSERT,UPDATE ON operation_checks TO pakodi_app;
    """)


def downgrade():
    op.execute("DROP TABLE operation_checks")
