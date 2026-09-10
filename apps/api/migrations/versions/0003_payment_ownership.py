"""Bind fulfillment to one capture and retain early delivery receipts."""

from alembic import op

revision = "0003_payment_ownership"
down_revision = "0002_commerce"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
      ALTER TABLE orders ADD COLUMN primary_payment_id uuid REFERENCES payments(id);
      ALTER TABLE orders ADD COLUMN invoiced_at timestamptz;
      ALTER TABLE payments ADD COLUMN post_started boolean NOT NULL DEFAULT false;
      CREATE TABLE message_receipts (
        id text PRIMARY KEY, brand_id text NOT NULL, status text NOT NULL,
        received_at timestamptz NOT NULL DEFAULT now());
      ALTER TABLE message_receipts ENABLE ROW LEVEL SECURITY;
      ALTER TABLE message_receipts FORCE ROW LEVEL SECURITY;
      CREATE POLICY brand_scope ON message_receipts TO pakodi_app
        USING (brand_id=current_setting('app.brand_id',true))
        WITH CHECK (brand_id=current_setting('app.brand_id',true));
      REVOKE ALL ON message_receipts FROM PUBLIC;
      GRANT SELECT,INSERT,UPDATE ON message_receipts TO pakodi_app;
    """)


def downgrade():
    op.execute("""
      DROP TABLE message_receipts;
      ALTER TABLE payments DROP COLUMN post_started;
      ALTER TABLE orders DROP COLUMN invoiced_at;
      ALTER TABLE orders DROP COLUMN primary_payment_id;
    """)
