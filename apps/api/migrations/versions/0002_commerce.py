"""Brand-scoped commerce, credentials, inventory and durable work."""

from alembic import op

revision = "0002_commerce"
down_revision = "0001_published_content"
branch_labels = None
depends_on = None

TABLES = (
    "admins",
    "sessions",
    "variants",
    "orders",
    "order_tokens",
    "payments",
    "refunds",
    "provider_events",
    "outbox",
    "enquiries",
    "media",
    "settings",
    "invoice_counters",
    "audit_events",
    "settlements",
)


def upgrade():
    op.execute("""

CREATE TABLE admins (
id uuid PRIMARY KEY, brand_id text NOT NULL, username text NOT NULL,
password_hash text NOT NULL, totp_secret text NOT NULL, enrolled boolean NOT
NULL DEFAULT false,
last_totp bigint NOT NULL DEFAULT -1, recovery_hashes jsonb NOT NULL DEFAULT
'[]',
enabled boolean NOT NULL DEFAULT true, UNIQUE(brand_id,username));
CREATE TABLE sessions (
id text PRIMARY KEY, brand_id text NOT NULL, admin_id uuid NOT NULL
REFERENCES admins(id),
csrf_hash text NOT NULL, expires_at timestamptz NOT NULL, revoked boolean
NOT NULL DEFAULT false);
CREATE TABLE media (
id uuid PRIMARY KEY, brand_id text NOT NULL, alt text NOT NULL,
created_at timestamptz NOT NULL DEFAULT now());
CREATE TABLE variants (
id uuid PRIMARY KEY, brand_id text NOT NULL, sku text NOT NULL, slug text
NOT NULL,
product jsonb NOT NULL, price_paise integer NOT NULL CHECK(price_paise>0),
gst_bps integer NOT NULL CHECK(gst_bps BETWEEN 0 AND 4000), hsn text NOT
NULL,
stock integer NOT NULL DEFAULT 0 CHECK(stock>=0), reserved integer NOT NULL
DEFAULT 0,
published boolean NOT NULL DEFAULT false, media_id uuid REFERENCES
media(id),
CHECK(reserved>=0 AND reserved<=stock), UNIQUE(brand_id,sku),
UNIQUE(brand_id,slug));
CREATE TABLE orders (
id uuid PRIMARY KEY, brand_id text NOT NULL, reference text NOT NULL UNIQUE,
request_key text NOT NULL, request_hash text NOT NULL, customer jsonb NOT
NULL,
lines jsonb NOT NULL, status text NOT NULL DEFAULT 'requested'
CHECK(status IN
('requested','approved','payment_pending','paid','dispatched','delivered','delivery_issue','declined','cancelled','refund_pending','refunded')),
consent boolean NOT NULL, consent_version text NOT NULL, created_at
timestamptz NOT NULL DEFAULT now(),
updated_at timestamptz NOT NULL DEFAULT now(), quote_version integer NOT
NULL DEFAULT 0,
quote_expires_at timestamptz, delivery_paise integer NOT NULL DEFAULT 0
CHECK(delivery_paise>=0),
total_paise integer NOT NULL DEFAULT 0 CHECK(total_paise>=0), tax jsonb NOT
NULL DEFAULT '{}',
seller jsonb NOT NULL DEFAULT '{}', reserved_until timestamptz,
reservation_active boolean NOT NULL DEFAULT false,
invoice_number text UNIQUE, delivered_at timestamptz, note text NOT NULL
DEFAULT '',
UNIQUE(brand_id,request_key));
CREATE TABLE order_tokens (
id text PRIMARY KEY, brand_id text NOT NULL, order_id uuid NOT NULL
REFERENCES orders(id),
expires_at timestamptz NOT NULL, revoked boolean NOT NULL DEFAULT false);
CREATE TABLE payments (
id uuid PRIMARY KEY, brand_id text NOT NULL, order_id uuid NOT NULL
REFERENCES orders(id),
quote_version integer NOT NULL, provider_order text UNIQUE, provider_payment
text UNIQUE,
status text NOT NULL DEFAULT 'creating', amount integer NOT NULL
CHECK(amount>0),
created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT
NULL DEFAULT now());
CREATE TABLE refunds (
id uuid PRIMARY KEY, brand_id text NOT NULL, payment_id uuid NOT NULL
REFERENCES payments(id),
order_id uuid NOT NULL REFERENCES orders(id), provider_id text UNIQUE,
amount integer NOT NULL CHECK(amount>0), status text NOT NULL DEFAULT
'pending',
reason text NOT NULL, created_at timestamptz NOT NULL DEFAULT now());
CREATE TABLE provider_events (
id text PRIMARY KEY, brand_id text NOT NULL, provider text NOT NULL,
payload text NOT NULL, processed boolean NOT NULL DEFAULT false,
created_at timestamptz NOT NULL DEFAULT now());
CREATE TABLE outbox (
id uuid PRIMARY KEY, brand_id text NOT NULL, kind text NOT NULL,
event_key text NOT NULL UNIQUE, payload text NOT NULL, order_id uuid
REFERENCES orders(id),
status text NOT NULL DEFAULT 'pending', attempts integer NOT NULL DEFAULT 0,
due_at timestamptz NOT NULL DEFAULT now(), lease_until timestamptz,
lease_id uuid, provider_id text, delivered_at timestamptz,
created_at timestamptz NOT NULL DEFAULT now(), last_error text NOT NULL
DEFAULT '');
CREATE TABLE enquiries (
id uuid PRIMARY KEY, brand_id text NOT NULL, details jsonb NOT NULL,
attribution jsonb NOT NULL, status text NOT NULL DEFAULT 'new'
CHECK(status IN ('new','contacted','qualified','won','lost')),
created_at timestamptz NOT NULL DEFAULT now());
CREATE TABLE settings (brand_id text PRIMARY KEY, data jsonb NOT NULL);
CREATE TABLE invoice_counters (brand_id text NOT NULL, period text NOT NULL,
value integer NOT NULL, PRIMARY KEY(brand_id,period));
CREATE TABLE audit_events (
id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, brand_id text NOT NULL,
actor text NOT NULL, action text NOT NULL, entity text NOT NULL,
changes jsonb NOT NULL, created_at timestamptz NOT NULL DEFAULT now());
CREATE TABLE settlements (
id text PRIMARY KEY, brand_id text NOT NULL, payload jsonb NOT NULL,
fetched_at timestamptz NOT NULL DEFAULT now());
CREATE INDEX order_status_idx ON orders(brand_id,status,created_at);
CREATE INDEX outbox_due_idx ON outbox(status,due_at);
CREATE INDEX tokens_order_idx ON order_tokens(order_id);
CREATE INDEX payments_order_idx ON payments(order_id);
CREATE INDEX refunds_order_idx ON refunds(order_id);

""")
    for table in TABLES:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
        op.execute(f"""CREATE POLICY brand_scope ON {table} TO pakodi_app
          USING (brand_id=current_setting('app.brand_id',true))
          WITH CHECK (brand_id=current_setting('app.brand_id',true))""")
        op.execute(f"REVOKE ALL ON {table} FROM PUBLIC")
        permissions = "SELECT,INSERT" if table == "audit_events" else "SELECT,INSERT,UPDATE"
        op.execute(f"GRANT {permissions} ON {table} TO pakodi_app")
    op.execute("GRANT USAGE ON SEQUENCE audit_events_id_seq TO pakodi_app")
    op.execute("""CREATE POLICY editorial_brand ON content_records TO pakodi_app
      USING (brand_id=current_setting('app.brand_id',true))
      WITH CHECK (brand_id=current_setting('app.brand_id',true))""")
    op.execute("GRANT SELECT,INSERT,UPDATE ON content_records TO pakodi_app")


def downgrade():
    op.execute("DROP POLICY editorial_brand ON content_records")
    op.execute("REVOKE SELECT,INSERT,UPDATE ON content_records FROM pakodi_app")
    for table in reversed(TABLES):
        op.execute(f"DROP TABLE {table} CASCADE")
