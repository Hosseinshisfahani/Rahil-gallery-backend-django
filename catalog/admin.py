from django.contrib import admin

from catalog.models import MaterialCategory, Product, ProductType, ProductVariant


@admin.register(MaterialCategory)
class MaterialCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "parent", "updated_at")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "updated_at")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("sku", "product", "updated_at")
    search_fields = ("sku",)
    autocomplete_fields = ("product",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "sku", "material_category", "product_type", "is_active")
    list_filter = ("is_active", "material_category", "product_type")
    search_fields = ("title", "sku", "slug")
    prepopulated_fields = {"slug": ("title",)}
