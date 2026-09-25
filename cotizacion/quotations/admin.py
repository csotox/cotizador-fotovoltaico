from django.contrib import admin

from .models import Quotation, QuotationItem


@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ("uuid", "company", "customer", "status", "total", "created_at")
    list_filter = ("status", "company")
    readonly_fields = ("uuid", "created_at", "updated_at", "deleted_at")
    search_fields = ("uuid", "customer__name")


@admin.register(QuotationItem)
class QuotationItemAdmin(admin.ModelAdmin):
    list_display = ("product_name", "quotation", "quantity", "unit_price", "subtotal")
    readonly_fields = ("uuid", "subtotal", "created_at", "updated_at")
    search_fields = ("product_name", "product_sku", "quotation__uuid")
