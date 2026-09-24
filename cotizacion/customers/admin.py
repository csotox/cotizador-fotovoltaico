from django.contrib import admin

from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "company",
        "email",
        "phone",
        "commune",
        "payment_method",
        "deleted_at",
    )
    search_fields = ("name", "email", "company__name")
    readonly_fields = ("uuid",)
