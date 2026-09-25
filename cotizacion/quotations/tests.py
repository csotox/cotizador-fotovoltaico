from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from companies.models import Company
from customers.models import Customer
from products.models import Product, ProductCategory, ProductKind, ProductUnit

from .models import Quotation, QuotationItem, QuotationStatus
from .services import (
    add_quotation_item,
    delete_quotation_item,
    update_quotation_item,
)


def make_user(username="vendedor"):
    return User.objects.create_user(username=username, password="clave-segura-123")


def make_company(created_by, suffix=""):
    return Company.objects.create(
        created_by=created_by,
        name=f"Compañía {suffix}",
        alias=f"C{suffix}",
        rut=f"12.345.678-{suffix or '5'}",
        email=f"company{suffix or '1'}@example.com",
    )


def make_customer(company, suffix=""):
    return Customer.objects.create(
        company=company,
        name=f"Cliente {suffix}",
        address="Dirección 123",
        email=f"customer{suffix or '1'}@example.com",
        phone="+56912345678",
        commune="Santiago",
        payment_method="cash",
    )


def make_product(company, name="Panel solar", price="120000", **kwargs):
    defaults = {
        "kind": ProductKind.PRODUCT,
        "category": ProductCategory.SOLAR_PANEL,
        "sku": "PANEL-001",
        "unit": ProductUnit.UNIT,
        "stock_quantity": 100,
    }
    defaults.update(kwargs)
    return Product.objects.create(
        company=company,
        name=name,
        unit_price=Decimal(price),
        **defaults,
    )


class QuotationModelTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.company = make_company(self.user)
        self.customer = make_customer(self.company)
        self.product = make_product(self.company)

    def test_defaults_and_uuid(self):
        quotation = Quotation.objects.create(company=self.company, customer=self.customer)
        item = add_quotation_item(quotation=quotation, product=self.product, quantity=2)

        self.assertEqual(quotation.status, QuotationStatus.DRAFT)
        self.assertEqual(quotation.total, Decimal("240000.00"))
        self.assertIsNotNone(quotation.uuid)
        self.assertIsNotNone(item.uuid)
        self.assertIsNotNone(quotation.created_at)
        self.assertIsNotNone(item.created_at)

    def test_soft_delete(self):
        quotation = Quotation.objects.create(company=self.company, customer=self.customer)
        quotation.delete()

        self.assertEqual(Quotation.objects.count(), 0)
        self.assertEqual(Quotation.objects.all_with_deleted().count(), 1)
        quotation.refresh_from_db()
        self.assertIsNotNone(quotation.deleted_at)

    def test_customer_must_belong_to_same_company(self):
        other_company = make_company(make_user("otro"), "2")
        other_customer = make_customer(other_company, "2")
        quotation = Quotation(company=self.company, customer=other_customer)

        with self.assertRaises(ValidationError):
            quotation.full_clean()


class QuotationServiceTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.company = make_company(self.user)
        self.customer = make_customer(self.company)
        self.quotation = Quotation.objects.create(company=self.company, customer=self.customer)
        self.panel = make_product(self.company)
        self.inverter = make_product(
            self.company,
            name="Inversor",
            price="650000",
            kind=ProductKind.SERVICE,
            category=ProductCategory.INVERTER,
            sku="INV-001",
            unit=ProductUnit.SERVICE,
            stock_quantity=None,
        )

    def test_add_item_copies_snapshot_and_calculates_amounts(self):
        item = add_quotation_item(quotation=self.quotation, product=self.panel, quantity=4)

        self.assertEqual(item.product_name, "Panel solar")
        self.assertEqual(item.product_sku, "PANEL-001")
        self.assertEqual(item.unit, ProductUnit.UNIT)
        self.assertEqual(item.unit_price, Decimal("120000.00"))
        self.assertEqual(item.subtotal, Decimal("480000.00"))
        self.quotation.refresh_from_db()
        self.assertEqual(self.quotation.total, Decimal("480000.00"))

    def test_product_changes_do_not_change_snapshot(self):
        item = add_quotation_item(quotation=self.quotation, product=self.panel, quantity=2)
        self.panel.name = "Panel actualizado"
        self.panel.sku = "PANEL-002"
        self.panel.unit_price = Decimal("150000")
        self.panel.save()

        item.refresh_from_db()
        self.assertEqual(item.product_name, "Panel solar")
        self.assertEqual(item.product_sku, "PANEL-001")
        self.assertEqual(item.unit_price, Decimal("120000.00"))
        self.assertEqual(item.subtotal, Decimal("240000.00"))

    def test_add_multiple_items_recalculates_total(self):
        add_quotation_item(quotation=self.quotation, product=self.panel, quantity=4)
        add_quotation_item(quotation=self.quotation, product=self.inverter, quantity=2)

        self.quotation.refresh_from_db()
        self.assertEqual(self.quotation.total, Decimal("1780000.00"))

    def test_update_item_recalculates_subtotal_and_total(self):
        item = add_quotation_item(quotation=self.quotation, product=self.panel, quantity=2)
        updated = update_quotation_item(item=item, product=self.inverter, quantity=3)

        self.assertEqual(updated.product_name, "Inversor")
        self.assertEqual(updated.subtotal, Decimal("1950000.00"))
        self.quotation.refresh_from_db()
        self.assertEqual(self.quotation.total, Decimal("1950000.00"))

    def test_delete_item_recalculates_total(self):
        first = add_quotation_item(quotation=self.quotation, product=self.panel, quantity=2)
        add_quotation_item(quotation=self.quotation, product=self.inverter, quantity=1)
        delete_quotation_item(first)

        self.quotation.refresh_from_db()
        self.assertEqual(self.quotation.total, Decimal("650000.00"))
        self.assertEqual(QuotationItem.objects.count(), 1)

    def test_rejects_non_positive_quantity(self):
        with self.assertRaises(ValidationError):
            add_quotation_item(quotation=self.quotation, product=self.panel, quantity=0)
        self.assertEqual(QuotationItem.objects.count(), 0)

    def test_rejects_inactive_product(self):
        self.panel.is_active = False
        self.panel.save()

        with self.assertRaises(ValidationError):
            add_quotation_item(quotation=self.quotation, product=self.panel, quantity=1)

    def test_rejects_deleted_product(self):
        self.panel.delete()

        with self.assertRaises(ValidationError):
            add_quotation_item(quotation=self.quotation, product=self.panel, quantity=1)

    def test_rejects_product_from_another_company(self):
        other_company = make_company(make_user("otro"), "2")
        other_product = make_product(other_company, name="Otro panel")

        with self.assertRaises(ValidationError):
            add_quotation_item(quotation=self.quotation, product=other_product, quantity=1)

    def test_rejects_item_changes_when_not_draft(self):
        item = add_quotation_item(quotation=self.quotation, product=self.panel, quantity=2)
        self.quotation.status = QuotationStatus.ISSUED
        self.quotation.save(update_fields=["status"])

        with self.assertRaises(ValidationError):
            update_quotation_item(item=item, product=self.panel, quantity=3)
        with self.assertRaises(ValidationError):
            delete_quotation_item(item)


class QuotationViewTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.company = make_company(self.user)
        self.customer = make_customer(self.company)
        self.product = make_product(self.company)
        self.client.force_login(self.user)

    def test_create_assigns_company_and_starts_as_draft(self):
        response = self.client.post(
            reverse("quotations:create"),
            {"customer": self.customer.uuid, "notes": "Instalación en empresa"},
        )
        self.assertEqual(response.status_code, 302)
        quotation = Quotation.objects.get()

        self.assertRedirects(
            response,
            reverse("quotations:detail", kwargs={"uuid": quotation.uuid}),
        )
        self.assertEqual(quotation.company, self.company)
        self.assertEqual(quotation.status, QuotationStatus.DRAFT)

    def test_create_rejects_customer_from_another_company(self):
        other_company = make_company(make_user("otro"), "2")
        other_customer = make_customer(other_company, "2")

        response = self.client.post(
            reverse("quotations:create"),
            {"customer": other_customer.uuid},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"],
            "customer",
            "Escoja una opción válida. Esa opción no está entre las disponibles.",
        )
        self.assertEqual(Quotation.objects.count(), 0)

    def test_list_and_detail_use_only_current_company(self):
        quotation = Quotation.objects.create(company=self.company, customer=self.customer)
        other_company = make_company(make_user("otro"), "2")
        other_customer = make_customer(other_company, "2")
        other_quotation = Quotation.objects.create(
            company=other_company,
            customer=other_customer,
        )

        list_response = self.client.get(reverse("quotations:list"))
        detail_response = self.client.get(
            reverse("quotations:detail", kwargs={"uuid": quotation.uuid})
        )
        hidden_response = self.client.get(
            reverse("quotations:detail", kwargs={"uuid": other_quotation.uuid})
        )

        self.assertEqual(list_response.status_code, 200)
        self.assertContains(list_response, quotation.uuid)
        self.assertNotContains(list_response, other_quotation.uuid)
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(hidden_response.status_code, 404)

    def test_item_create_modal_returns_partial(self):
        quotation = Quotation.objects.create(company=self.company, customer=self.customer)
        url = reverse("quotations:item-create", kwargs={"uuid": quotation.uuid})

        response = self.client.get(url, {"form": "modal"})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "quotations/_item_form.html")
        self.assertNotContains(response, "<html")
        self.assertContains(response, "<form")

    def test_item_create_modal_returns_json_on_success(self):
        quotation = Quotation.objects.create(company=self.company, customer=self.customer)
        url = reverse("quotations:item-create", kwargs={"uuid": quotation.uuid})

        response = self.client.post(
            url,
            {"product": self.product.uuid, "quantity": "4", "form": "modal"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"success": True})
        self.assertEqual(QuotationItem.objects.count(), 1)

    def test_item_create_modal_keeps_form_open_on_error(self):
        quotation = Quotation.objects.create(company=self.company, customer=self.customer)
        url = reverse("quotations:item-create", kwargs={"uuid": quotation.uuid})

        response = self.client.post(
            url,
            {"product": self.product.uuid, "quantity": "", "form": "modal"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "quotations/_item_form.html")
        self.assertContains(response, "Este campo es obligatorio.")
        self.assertEqual(QuotationItem.objects.count(), 0)

    def test_item_create_copies_product_and_calculates_total(self):
        quotation = Quotation.objects.create(company=self.company, customer=self.customer)
        url = reverse("quotations:item-create", kwargs={"uuid": quotation.uuid})

        response = self.client.post(url, {"product": self.product.uuid, "quantity": "4"})
        item = QuotationItem.objects.get()
        quotation.refresh_from_db()

        self.assertRedirects(
            response,
            reverse("quotations:detail", kwargs={"uuid": quotation.uuid}),
        )
        self.assertEqual(item.product_name, self.product.name)
        self.assertEqual(item.subtotal, Decimal("480000.00"))
        self.assertEqual(quotation.total, Decimal("480000.00"))

    def test_item_create_rejects_product_from_another_company(self):
        other_company = make_company(make_user("otro"), "2")
        other_product = make_product(other_company, name="Otro panel")
        quotation = Quotation.objects.create(company=self.company, customer=self.customer)

        response = self.client.post(
            reverse("quotations:item-create", kwargs={"uuid": quotation.uuid}),
            {"product": other_product.uuid, "quantity": "1"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(QuotationItem.objects.count(), 0)

    def test_detail_uses_snapshot_after_product_changes(self):
        quotation = Quotation.objects.create(company=self.company, customer=self.customer)
        add_quotation_item(quotation=quotation, product=self.product, quantity=1)
        self.product.name = "Producto nuevo"
        self.product.unit_price = Decimal("200000")
        self.product.save()

        response = self.client.get(
            reverse("quotations:detail", kwargs={"uuid": quotation.uuid})
        )

        self.assertContains(response, "Panel solar")
        self.assertNotContains(response, "Producto nuevo")
        self.assertContains(response, "120000,00")

    def test_item_update_and_delete_recalculate_total(self):
        quotation = Quotation.objects.create(company=self.company, customer=self.customer)
        item = add_quotation_item(quotation=quotation, product=self.product, quantity=1)
        update_url = reverse(
            "quotations:item-update",
            kwargs={"uuid": quotation.uuid, "item_uuid": item.uuid},
        )
        delete_url = reverse(
            "quotations:item-delete",
            kwargs={"uuid": quotation.uuid, "item_uuid": item.uuid},
        )

        response = self.client.post(update_url, {"product": self.product.uuid, "quantity": "2"})
        item.refresh_from_db()
        quotation.refresh_from_db()

        self.assertRedirects(
            response,
            reverse("quotations:detail", kwargs={"uuid": quotation.uuid}),
        )
        self.assertEqual(item.subtotal, Decimal("240000.00"))
        self.assertEqual(quotation.total, Decimal("240000.00"))

        response = self.client.post(delete_url)
        quotation.refresh_from_db()

        self.assertRedirects(
            response,
            reverse("quotations:detail", kwargs={"uuid": quotation.uuid}),
        )
        self.assertEqual(QuotationItem.objects.count(), 0)
        self.assertEqual(quotation.total, Decimal("0.00"))

    def test_non_draft_quotation_does_not_allow_item_changes(self):
        quotation = Quotation.objects.create(
            company=self.company,
            customer=self.customer,
        )
        item = add_quotation_item(quotation=quotation, product=self.product, quantity=1)
        quotation.status = QuotationStatus.ISSUED
        quotation.save(update_fields=["status"])
        add_url = reverse("quotations:item-create", kwargs={"uuid": quotation.uuid})
        update_url = reverse(
            "quotations:item-update",
            kwargs={"uuid": quotation.uuid, "item_uuid": item.uuid},
        )
        delete_url = reverse(
            "quotations:item-delete",
            kwargs={"uuid": quotation.uuid, "item_uuid": item.uuid},
        )

        self.assertEqual(self.client.get(add_url).status_code, 403)
        self.assertEqual(self.client.get(update_url).status_code, 403)
        self.assertEqual(self.client.post(delete_url).status_code, 403)

    def test_quotation_delete_is_soft_and_post_only(self):
        quotation = Quotation.objects.create(company=self.company, customer=self.customer)
        url = reverse("quotations:delete", kwargs={"uuid": quotation.uuid})

        self.assertEqual(self.client.get(url).status_code, 405)
        response = self.client.post(url)

        self.assertRedirects(response, reverse("quotations:list"))
        quotation.refresh_from_db()
        self.assertIsNotNone(quotation.deleted_at)

    def test_urls_use_public_uuids(self):
        quotation = Quotation.objects.create(company=self.company, customer=self.customer)
        item = add_quotation_item(quotation=quotation, product=self.product, quantity=1)

        detail_url = reverse("quotations:detail", kwargs={"uuid": quotation.uuid})
        item_url = reverse(
            "quotations:item-update",
            kwargs={"uuid": quotation.uuid, "item_uuid": item.uuid},
        )

        self.assertEqual(detail_url, f"/quotations/{quotation.uuid}/")
        self.assertNotIn(f"/{quotation.id}/", detail_url)
        self.assertNotIn(f"/{item.id}/", item_url)
