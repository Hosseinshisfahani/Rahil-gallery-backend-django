import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0003_productvariant_managed"),
        ("commerce", "0001_initial"),
    ]

    operations = [
        # variant_id was a uuid column aimed at the old unmanaged variant.
        # The managed skeleton uses a bigint primary key, and those uuid
        # values cannot be carried over.
        migrations.RunSQL(
            sql="""
            DO $$
            DECLARE r record;
            BEGIN
                FOR r IN
                    SELECT c.conname, t.relname
                    FROM pg_constraint c
                    JOIN pg_class t ON t.oid = c.conrelid
                    JOIN pg_namespace n ON n.oid = t.relnamespace
                    JOIN pg_attribute a
                      ON a.attrelid = t.oid AND a.attnum = ANY (c.conkey)
                    WHERE c.contype = 'f'
                      AND n.nspname = current_schema()
                      AND t.relname IN ('cart_items', 'order_items')
                      AND a.attname = 'variant_id'
                LOOP
                    EXECUTE format(
                        'ALTER TABLE %I DROP CONSTRAINT %I',
                        r.relname,
                        r.conname
                    );
                END LOOP;
            END $$;
            ALTER TABLE cart_items DROP CONSTRAINT IF EXISTS cart_items_unique_variant;
            DELETE FROM cart_items;
            DELETE FROM order_items;
            ALTER TABLE cart_items ALTER COLUMN variant_id TYPE bigint USING NULL;
            ALTER TABLE order_items ALTER COLUMN variant_id TYPE bigint USING NULL;
            ALTER TABLE cart_items
                ADD CONSTRAINT cart_items_unique_variant UNIQUE (cart_id, variant_id);
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.AlterField(
            model_name="cartitem",
            name="variant",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="cart_items",
                to="catalog.productvariant",
            ),
        ),
        migrations.AlterField(
            model_name="orderitem",
            name="variant",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="order_items",
                to="catalog.productvariant",
            ),
        ),
    ]
