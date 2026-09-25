from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from companies.models import Company

from .models import Product, ProductCategory, ProductKind, ProductUnit


VALID_RUT = "12.345.678-5"


def make_user(username="vendedor"):
    return User.objects.create_user(username=username, password="clave-segura-123")


def make_company(created_by, **overrides):
    values = {
        "name": "Energía Solar SpA",
        "alias": "ES",
        "address": "Av. Siempre Viva 123",
        "rut": VALID_RUT,
        "email": "contacto@energiasolar.cl",
    }
    values.update(overrides)
    return Company.objects.create(created_by=created_by, **values)


def product_data(**overrides):
    data = {
        "kind": ProductKind.PRODUCT,
        "category": ProductCategory.SOLAR_PANEL,
        "name": "Panel JA Solar 550 W",
        "description": "Panel fotovoltaico",
        "sku": "PANEL-JA-550",
        "manufacturer": "JA Solar",
        "model": "JAM60S20-550/MR",
        "unit_price": "45000.00",
        "unit": ProductUnit.UNIT,
        "stock_quantity": "10",
        "technical_specs": '{"rated_power_w": 550}',
        "is_active": "on",
    }
    data.update(overrides)
    return data


class ProductModelTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.company = make_company(self.user)

    def test_uuid_timestamps_and_defaults_are_set(self):
        product = Product.objects.create(
            company=self.company,
            kind=ProductKind.PRODUCT,
            category=ProductCategory.SOLAR_PANEL,
            name="Panel",
            unit_price=Decimal("45000.00"),
            stock_quantity=10,
        )
        self.assertIsNotNone(product.uuid)
        self.assertIsNotNone(product.created_at)
        self.assertIsNotNone(product.updated_at)
        self.assertTrue(product.is_active)
        self.assertEqual(product.unit, ProductUnit.UNIT)
        self.assertEqual(product.technical_specs, {})

    def test_delete_is_soft(self):
        product = Product.objects.create(
            company=self.company,
            kind=ProductKind.SERVICE,
            category=ProductCategory.INSTALLATION,
            name="Instalación",
            unit_price=Decimal("100000.00"),
        )
        product.delete()
        product.refresh_from_db()
        self.assertIsNotNone(product.deleted_at)
        self.assertEqual(Product.objects.count(), 0)
        self.assertEqual(Product.objects.all_with_deleted().count(), 1)


class ProductFormValidationTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.company = make_company(self.user)
        self.client.force_login(self.user)

    def test_duplicate_sku_in_company_is_rejected(self):
        Product.objects.create(
            company=self.company,
            kind=ProductKind.PRODUCT,
            category=ProductCategory.SOLAR_PANEL,
            name="Otro panel",
            sku="PANEL-JA-550",
            unit_price=Decimal("45000.00"),
            stock_quantity=1,
        )
        response = self.client.post(reverse("products:create"), product_data(sku="panel-ja-550"))
        self.assertFormError(
            response.context["form"],
            "sku",
            "Ya existe un elemento con este SKU en la compañía.",
        )

    def test_product_requires_stock(self):
        response = self.client.post(reverse("products:create"), product_data(stock_quantity=""))
        self.assertFormError(
            response.context["form"],
            "stock_quantity",
            "El stock es obligatorio para productos.",
        )

    def test_consumable_stock_is_cleared(self):
        response = self.client.post(
            reverse("products:create"),
            product_data(kind=ProductKind.CONSUMABLE, category=ProductCategory.CABLE, stock_quantity="5"),
        )
        self.assertEqual(response.status_code, 302)
        self.assertIsNone(Product.objects.get().stock_quantity)

    def test_invalid_technical_specs_are_rejected(self):
        response = self.client.post(
            reverse("products:create"),
            product_data(technical_specs="not-json"),
        )
        self.assertFormError(
            response.context["form"],
            "technical_specs",
            "Ingresa un JSON válido.",
        )


class ProductViewTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.company = make_company(self.user)
        self.client.force_login(self.user)

    def test_list_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("products:list"))
        self.assertEqual(response.status_code, 302)

    def test_list_is_scoped_to_company(self):
        other_user = make_user("other")
        other_company = make_company(
            other_user,
            name="Otra Compañía",
            rut="11.111.111-1",
            email="otra@ejemplo.cl",
        )
        Product.objects.create(
            company=self.company,
            kind=ProductKind.PRODUCT,
            category=ProductCategory.SOLAR_PANEL,
            name="Panel propio",
            unit_price=Decimal("45000.00"),
            stock_quantity=1,
        )
        Product.objects.create(
            company=other_company,
            kind=ProductKind.SERVICE,
            category=ProductCategory.INSTALLATION,
            name="Servicio ajeno",
            unit_price=Decimal("100000.00"),
        )
        response = self.client.get(reverse("products:list"))
        self.assertContains(response, "Panel propio")
        self.assertNotContains(response, "Servicio ajeno")

    def test_create_assigns_company_and_redirects_to_detail(self):
        response = self.client.post(reverse("products:create"), product_data())
        product = Product.objects.get()
        self.assertRedirects(
            response,
            reverse("products:detail", kwargs={"uuid": product.uuid}),
        )
        self.assertEqual(product.company, self.company)

    def test_update_and_delete_use_uuid(self):
        product = Product.objects.create(
            company=self.company,
            kind=ProductKind.PRODUCT,
            category=ProductCategory.SOLAR_PANEL,
            name="Panel original",
            unit_price=Decimal("45000.00"),
            stock_quantity=1,
        )
        detail_url = reverse("products:detail", kwargs={"uuid": product.uuid})
        update_url = reverse("products:update", kwargs={"uuid": product.uuid})
        self.assertEqual(self.client.get(detail_url).status_code, 200)
        response = self.client.post(update_url, product_data(name="Panel actualizado"))
        self.assertRedirects(response, detail_url)
        product.refresh_from_db()
        self.assertEqual(product.name, "Panel actualizado")
        response = self.client.post(reverse("products:delete", kwargs={"uuid": product.uuid}))
        self.assertRedirects(response, reverse("products:list"))
        product.refresh_from_db()
        self.assertIsNotNone(product.deleted_at)

    def test_other_user_cannot_access_product(self):
        product = Product.objects.create(
            company=self.company,
            kind=ProductKind.PRODUCT,
            category=ProductCategory.SOLAR_PANEL,
            name="Panel privado",
            unit_price=Decimal("45000.00"),
            stock_quantity=1,
        )
        make_user("other")
        self.client.force_login(User.objects.get(username="other"))
        response = self.client.get(
            reverse("products:detail", kwargs={"uuid": product.uuid})
        )
        self.assertEqual(response.status_code, 302)

    def test_staff_is_forbidden(self):
        staff = User.objects.create_user(
            username="staff", password="clave-segura-123", is_staff=True
        )
        self.client.force_login(staff)
        response = self.client.get(reverse("products:list"))
        self.assertEqual(response.status_code, 403)


class ProductModalTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.company = make_company(self.user)
        self.client.force_login(self.user)

    def test_create_modal_returns_partial(self):
        response = self.client.get(reverse("products:create"), {"form": "modal"})
        self.assertTemplateUsed(response, "products/_form.html")
        self.assertNotContains(response, "<html")
        self.assertContains(response, "<form")

    def test_create_modal_returns_json(self):
        response = self.client.post(
            reverse("products:create"),
            product_data(form="modal"),
        )
        self.assertEqual(response.json(), {"success": True})
        self.assertEqual(Product.objects.count(), 1)


class ProductOnboardingTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.client.force_login(self.user)

    def test_all_product_views_redirect_without_company(self):
        product_uuid = "00000000-0000-0000-0000-000000000002"
        urls = [
            reverse("products:list"),
            reverse("products:create"),
            reverse("products:detail", kwargs={"uuid": product_uuid}),
            reverse("products:update", kwargs={"uuid": product_uuid}),
            reverse("products:delete", kwargs={"uuid": product_uuid}),
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertRedirects(response, reverse("home"))
            self.assertContains(self.client.get(reverse("home")), "Configura tu espacio comercial")
