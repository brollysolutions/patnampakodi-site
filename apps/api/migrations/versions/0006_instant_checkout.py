"""Additive instant checkout and one pilot fresh outlet; legacy orders remain valid."""

from alembic import op

revision = "0006_instant_checkout"
down_revision = "0005_quick_enquiries"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
ALTER TABLE orders ADD COLUMN shopping_mode text NOT NULL DEFAULT 'packaged'
    CHECK(shopping_mode IN ('packaged','fresh')),
    ADD COLUMN checkout_kind text NOT NULL DEFAULT 'staff'
    CHECK(checkout_kind IN ('staff','instant')),
    ADD COLUMN fulfilment jsonb NOT NULL DEFAULT '{}';
ALTER TABLE orders DROP CONSTRAINT orders_status_check;
ALTER TABLE orders ADD CONSTRAINT orders_status_check CHECK(status IN
('requested','approved','payment_pending','paid','preparing','dispatched','delivered',
'delivery_issue','declined','cancelled','refund_pending','refunded'));
CREATE TABLE fulfilment_settings (brand_id text PRIMARY KEY, data jsonb NOT NULL);
ALTER TABLE fulfilment_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE fulfilment_settings FORCE ROW LEVEL SECURITY;
CREATE POLICY brand_scope ON fulfilment_settings TO pakodi_app
USING (brand_id=current_setting('app.brand_id',true))
WITH CHECK (brand_id=current_setting('app.brand_id',true));
REVOKE ALL ON fulfilment_settings FROM PUBLIC;
GRANT SELECT,INSERT,UPDATE ON fulfilment_settings TO pakodi_app;
""")
    op.execute("""
ALTER TABLE content_records DROP CONSTRAINT published_product_complete;
ALTER TABLE content_records ADD CONSTRAINT published_product_complete CHECK (
NOT (published AND kind='product') OR (
payload ?& ARRAY['slug','name','description','price_paise','dietary','ingredients',
'allergens','nutrition','net_quantity','consumer_care']
AND jsonb_typeof(payload->'price_paise')='number' AND (payload->>'price_paise')::numeric>0
AND payload->>'dietary' IN ('veg','non-veg')
AND jsonb_path_query_array(payload,
'$.keyvalue() ? (@.key == "slug" || @.key == "name" || @.key == "description" ||
@.key == "ingredients" || @.key == "allergens" || @.key == "nutrition" ||
@.key == "net_quantity" || @.key == "consumer_care").value')
<@ jsonb_path_query_array(payload, '$.* ? (@.type() == "string" && @ like_regex "[^\\\\s]")')
AND (
(COALESCE(payload->>'mode','packaged')='packaged'
AND jsonb_typeof(payload->'shelf_life')='string' AND payload->>'shelf_life' ~ '[^[:space:]]'
AND jsonb_typeof(payload->'manufacturer')='string' AND payload->>'manufacturer' ~ '[^[:space:]]')
OR (payload->>'mode'='fresh' AND jsonb_typeof(payload->'outlet_slug')='string'
AND payload->>'outlet_slug' ~ '^[a-z0-9]+(-[a-z0-9]+)*$'))
) IS TRUE);
""")


def downgrade():
    # Refuse a downgrade that would misclassify fresh purchases or lose their configuration.
    op.execute("""DO $$ BEGIN
IF EXISTS (SELECT 1 FROM orders WHERE checkout_kind='instant') OR
EXISTS (SELECT 1 FROM content_records WHERE kind='product' AND payload->>'mode'='fresh') OR
EXISTS (SELECT 1 FROM variants WHERE product->>'mode'='fresh') THEN
RAISE EXCEPTION 'Retain migration: instant checkout orders exist'; END IF; END $$;""")
    op.execute("DROP TABLE fulfilment_settings")
    op.execute("""ALTER TABLE content_records DROP CONSTRAINT published_product_complete;
ALTER TABLE content_records ADD CONSTRAINT published_product_complete CHECK (
                NOT (published AND kind = 'product') OR (
                    payload ?& ARRAY['slug','name','description','price_paise','dietary',
                        'ingredients','allergens','nutrition','net_quantity','shelf_life',
                        'manufacturer','consumer_care']
                    AND jsonb_typeof(payload->'price_paise') = 'number'
                    AND (payload->>'price_paise')::numeric > 0
                    AND payload->>'dietary' IN ('veg', 'non-veg')
                    AND jsonb_path_query_array(payload,
                        '$.keyvalue() ? (@.key == "slug" || @.key == "name" ||
                         @.key == "description" || @.key == "ingredients" ||
                         @.key == "allergens" || @.key == "nutrition" ||
                         @.key == "net_quantity" || @.key == "shelf_life" ||
                         @.key == "manufacturer" || @.key == "consumer_care").value'
                    ) <@ jsonb_path_query_array(payload,
                        '$.* ? (@.type() == "string" && @ like_regex "[^\\\\s]")')
                ) IS TRUE
            );
""")
    op.execute("ALTER TABLE orders DROP CONSTRAINT orders_status_check")
    op.execute("""ALTER TABLE orders ADD CONSTRAINT orders_status_check CHECK(status IN
('requested','approved','payment_pending','paid','dispatched','delivered','delivery_issue',
'declined','cancelled','refund_pending','refunded'))""")
    op.execute(
        "ALTER TABLE orders DROP COLUMN shopping_mode, DROP COLUMN checkout_kind, "
        "DROP COLUMN fulfilment"
    )
