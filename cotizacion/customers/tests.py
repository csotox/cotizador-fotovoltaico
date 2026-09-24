from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from companies.models import Company

from .models import Customer

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


def make_customer(company, **kwargs):
    defaults = {
        "name": "Cliente Solar SpA",
        "address": "Av. Cliente 123",
        "email": "cliente@example.com",
        "phone": "+56912345678",
        "commune": "Santiago",
        "payment_method": "bank_transfer",
    }
    defaults.update(kwargs)
    return Customer.objects.create(company=company, **defaults)


def customer_data(**overrides):
    data = {
        "name": "Cliente Solar SpA",
        "address": "Av. Cliente 123",
        "email": "cliente@example.com",
        "phone": "+56912345678",
        "commune": "Santiago",
        "payment_method": "bank_transfer",
    }
    data.update(overrides)
    return data


class CustomerModelTests(TestCase):
    def test_uuid_and_timestamps_are_set(self):
        customer = make_customer(make_company(make_user()))
        self.assertIsNotNone(customer.uuid)
        self.assertIsNotNone(customer.created_at)
        self.assertIsNotNone(customer.updated_at)

    def test_delete_is_soft(self):
        customer = make_customer(make_company(make_user()))
        customer.delete()
        customer.refresh_from_db()
        self.assertIsNotNone(customer.deleted_at)
        self.assertEqual(Customer.objects.count(), 0)
        self.assertEqual(Customer.objects.all_with_deleted().count(), 1)


class CustomerFormValidationTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.company = make_company(self.user)
        self.client.force_login(self.user)

    def test_duplicate_email_in_company_is_rejected(self):
        make_customer(self.company)
        response = self.client.post(
            reverse("customers:create"), customer_data(email="CLIENTE@EXAMPLE.COM")
        )
        self.assertFormError(
            response.context["form"],
            "email",
            "Ya existe un cliente con este correo en la compañía.",
        )

    def test_email_is_normalized(self):
        response = self.client.post(
            reverse("customers:create"), customer_data(email="CLIENTE@EXAMPLE.COM")
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Customer.objects.get().email, "cliente@example.com")

    def test_invalid_payment_method_is_rejected(self):
        response = self.client.post(
            reverse("customers:create"), customer_data(payment_method="unknown")
        )
        self.assertFormError(
            response.context["form"],
            "payment_method",
            "Escoja una opción válida. unknown no es una de las opciones disponibles.",
        )


class CustomerViewTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.company = make_company(self.user)
        self.client.force_login(self.user)

    def test_list_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("customers:list"))
        self.assertEqual(response.status_code, 302)

    def test_list_shows_only_company_customers(self):
        other_user = make_user("other")
        other_company = make_company(
            other_user,
            name="Otra Compañía",
            rut="11.111.111-1",
            email="otra@ejemplo.cl",
        )
        make_customer(self.company)
        make_customer(other_company, email="other@example.com")
        response = self.client.get(reverse("customers:list"))
        self.assertContains(response, "cliente@example.com")
        self.assertNotContains(response, "other@example.com")

    def test_create_assigns_company_and_redirects_to_detail(self):
        response = self.client.post(reverse("customers:create"), customer_data())
        customer = Customer.objects.get()
        self.assertRedirects(
            response,
            reverse("customers:detail", kwargs={"uuid": customer.uuid}),
        )
        self.assertEqual(customer.company, self.company)

    def test_detail_and_update_use_uuid_and_owner_scope(self):
        customer = make_customer(self.company)
        detail_url = reverse("customers:detail", kwargs={"uuid": customer.uuid})
        update_url = reverse("customers:update", kwargs={"uuid": customer.uuid})
        self.assertIn(str(customer.uuid), detail_url)
        self.assertEqual(self.client.get(detail_url).status_code, 200)
        response = self.client.post(update_url, customer_data(name="Actualizado"))
        self.assertRedirects(response, detail_url)
        customer.refresh_from_db()
        self.assertEqual(customer.name, "Actualizado")

    def test_other_user_cannot_access_customer(self):
        customer = make_customer(self.company)
        make_user("other")
        self.client.force_login(User.objects.get(username="other"))
        response = self.client.get(
            reverse("customers:detail", kwargs={"uuid": customer.uuid})
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_is_soft_and_redirects_to_list(self):
        customer = make_customer(self.company)
        response = self.client.post(
            reverse("customers:delete", kwargs={"uuid": customer.uuid})
        )
        self.assertRedirects(response, reverse("customers:list"))
        customer.refresh_from_db()
        self.assertIsNotNone(customer.deleted_at)

    def test_staff_is_forbidden(self):
        staff = User.objects.create_user(
            username="staff", password="clave-segura-123", is_staff=True
        )
        self.client.force_login(staff)
        response = self.client.get(reverse("customers:list"))
        self.assertEqual(response.status_code, 403)


class CustomerModalTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.company = make_company(self.user)
        self.client.force_login(self.user)

    def test_create_modal_returns_partial(self):
        response = self.client.get(reverse("customers:create"), {"form": "modal"})
        self.assertTemplateUsed(response, "customers/_form.html")
        self.assertNotContains(response, "<html")
        self.assertContains(response, "<form")

    def test_create_modal_returns_json(self):
        response = self.client.post(
            reverse("customers:create"),
            customer_data(form="modal"),
        )
        self.assertEqual(response.json(), {"success": True})
        self.assertEqual(Customer.objects.count(), 1)
