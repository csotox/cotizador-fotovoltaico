from django.contrib import admin

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "kind", "category", "is_active")
    list_filter = ("kind", "category", "is_active")
    search_fields = ("name", "sku", "manufacturer", "model")
    readonly_fields = ("uuid",)
