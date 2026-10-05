import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0002_material_category_product_type"),
    ]

    operations = [
        # Previous ProductVariant mapped Go's product_variants table and was
        # unmanaged. Drop it from Django state only so migrate does not DROP
        # that table, then create the Django-owned skeleton.
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.DeleteModel(name="ProductVariant"),
            ],
            database_operations=[],
        ),
        migrations.CreateModel(
            name="ProductVariant",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "sku",
                    models.CharField(
                        blank=True,
                        max_length=50,
                        null=True,
                        unique=True,
                        verbose_name="SKU",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="created at"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="updated at"),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="variants",
                        to="catalog.product",
                        verbose_name="product",
                    ),
                ),
            ],
            options={
                "verbose_name": "product variant",
                "verbose_name_plural": "product variants",
            },
        ),
    ]
