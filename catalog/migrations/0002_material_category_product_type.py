import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0001_initial"),
    ]

    operations = [
        # Previous Product was an unmanaged mapping of Go's products table.
        # Drop it from Django state only so migrate does not DROP that table.
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.DeleteModel(name="Product"),
            ],
            database_operations=[],
        ),
        migrations.CreateModel(
            name="MaterialCategory",
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
                ("name", models.CharField(max_length=255, verbose_name="name")),
                (
                    "slug",
                    models.SlugField(
                        allow_unicode=True,
                        max_length=255,
                        unique=True,
                        verbose_name="slug",
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
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sub_materials",
                        to="catalog.materialcategory",
                        verbose_name="parent",
                    ),
                ),
            ],
            options={
                "verbose_name": "material category",
                "verbose_name_plural": "material categories",
            },
        ),
        migrations.CreateModel(
            name="ProductType",
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
                ("name", models.CharField(max_length=255, verbose_name="name")),
                (
                    "slug",
                    models.SlugField(
                        allow_unicode=True,
                        max_length=255,
                        unique=True,
                        verbose_name="slug",
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
            ],
            options={
                "verbose_name": "product type",
                "verbose_name_plural": "product types",
            },
        ),
        migrations.CreateModel(
            name="Product",
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
                ("title", models.CharField(max_length=255, verbose_name="title")),
                (
                    "slug",
                    models.SlugField(
                        allow_unicode=True,
                        max_length=255,
                        unique=True,
                        verbose_name="slug",
                    ),
                ),
                (
                    "sku",
                    models.CharField(max_length=64, unique=True, verbose_name="SKU"),
                ),
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="is active"),
                ),
                (
                    "description",
                    models.TextField(blank=True, verbose_name="description"),
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
                    "material_category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="products",
                        to="catalog.materialcategory",
                        verbose_name="material category",
                    ),
                ),
                (
                    "product_type",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="products",
                        to="catalog.producttype",
                        verbose_name="product type",
                    ),
                ),
            ],
            options={
                "verbose_name": "product",
                "verbose_name_plural": "products",
            },
        ),
    ]
