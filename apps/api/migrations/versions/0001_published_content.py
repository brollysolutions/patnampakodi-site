"""Published content with a read-only, brand-scoped public role."""

from alembic import op

revision = "0001_published_content"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE content_records (
            brand_id text NOT NULL,
            kind text NOT NULL CHECK (
                kind IN ('brand','page','menu','outlet','franchise','product')),
            slug text NOT NULL,
            position integer NOT NULL DEFAULT 0,
            published boolean NOT NULL DEFAULT false,
            payload jsonb NOT NULL CHECK (jsonb_typeof(payload) = 'object'),
            PRIMARY KEY (brand_id, kind, slug),
            CONSTRAINT published_product_complete CHECK (
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
            )
        )
    """)
    op.execute("ALTER TABLE content_records ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE content_records FORCE ROW LEVEL SECURITY")
    op.execute("""
        CREATE POLICY published_brand_content ON content_records FOR SELECT
        TO pakodi_reader USING (
            published = true AND brand_id = current_setting('app.brand_id', true)
        )
    """)
    op.execute("REVOKE ALL ON content_records FROM PUBLIC")
    op.execute("GRANT SELECT ON content_records TO pakodi_reader")


def downgrade() -> None:
    op.execute("DROP TABLE content_records")
