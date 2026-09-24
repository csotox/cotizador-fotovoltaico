from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Company

VALID_RUT = "12.345.678-5"


def make_user(username="vendedor"):
    return User.objects.create_user(username=username, password="clave-segura-123")


def make_company(created_by, **kwargs):
    defaults = {
        "name": "Energía Solar SpA",
        "alias": "ES",
        "address": "Av. Siempre Viva 123",
        "rut": VALID_RUT,
        "email": "contacto@energiasolar.cl",
    }
    defaults.update(kwargs)
    return Company.objects.create(created_by=created_by, **defaults)


class CompanyModelTests(TestCase):
    def test_uuid_auto_generated_and_unique(self):
        user = make_user()
        first = make_company(created_by=user, email="a@example.com", rut="12.345.678-5")
        second = make_company(created_by=user, email="b@example.com", rut="11.111.111-1")
        self.assertIsNotNone(first.uuid)
        self.assertNotEqual(first.uuid, second.uuid)

    def test_created_at_and_updated_at_set(self):
        company = make_company(created_by=make_user())
        self.assertIsNotNone(company.created_at)
        self.assertIsNotNone(company.updated_at)


class SoftDeleteTests(TestCase):
    def test_delete_soft_deletes(self):
        company = make_company(created_by=make_user())
        company.delete()
        company.refresh_from_db()
        self.assertIsNotNone(company.deleted_at)
        self.assertEqual(Company.objects.count(), 0)
        self.assertEqual(Company.objects.all_with_deleted().count(), 1)

    def test_default_queryset_excludes_deleted(self):
        user = make_user()
        alive = make_company(created_by=user)
        deleted = make_company(created_by=user, email="b@example.com", rut="11.111.111-1")
        deleted.delete()
        self.assertEqual(list(Company.objects.all()), [alive])

    def test_dead_returns_only_deleted(self):
        user = make_user()
        alive = make_company(created_by=user)
        deleted = make_company(created_by=user, email="b@example.com", rut="11.111.111-1")
        deleted.delete()
        dead = list(Company.objects.dead())
        self.assertEqual(dead, [deleted])
        self.assertNotIn(alive, dead)

    def test_hard_delete_removes_row(self):
        company = make_company(created_by=make_user())
        company.hard_delete()
        self.assertEqual(Company.objects.all_with_deleted().count(), 0)

    def test_queryset_delete_soft_deletes(self):
        user = make_user()
        company = make_company(created_by=user)
        Company.objects.filter(pk=company.pk).delete()
        self.assertEqual(Company.objects.count(), 0)
        self.assertEqual(Company.objects.all_with_deleted().count(), 1)


class CompanyFormValidationTests(TestCase):
    def _post(self, **overrides):
        data = {
            "name": "Energía Solar SpA",
            "alias": "ES",
            "address": "Av. Siempre Viva 123",
            "rut": VALID_RUT,
            "email": "contacto@energiasolar.cl",
        }
        data.update(overrides)
        return self.client.post(reverse("companies:create"), data)

    def setUp(self):
        self.user = make_user()
        self.client.force_login(self.user)

    def test_blank_name_rejected(self):
        response = self._post(name="")
        self.assertFormError(response.context["form"], "name", "Este campo es obligatorio.")

    def test_invalid_rut_rejected(self):
        response = self._post(rut="76.123.456-7")
        self.assertFormError(
            response.context["form"], "rut", "El RUT ingresado no es válido."
        )

    def test_rut_requires_alphanumeric_format(self):
        response = self._post(rut="no-es-un-rut")
        self.assertFormError(response.context["form"], "rut", "Ingresa un RUT válido.")

    def test_duplicate_rut_rejected(self):
        make_company(created_by=self.user)
        response = self._post(name="Otra Empresa", email="otra@example.com")
        self.assertFormError(
            response.context["form"], "rut", "Ya existe una empresa con este RUT."
        )

    def test_blank_email_rejected(self):
        response = self._post(email="")
        self.assertFormError(response.context["form"], "email", "Este campo es obligatorio.")

    def test_invalid_email_rejected(self):
        response = self._post(email="correo-invalido")
        self.assertFormError(
            response.context["form"], "email", "Introduzca una dirección de correo electrónico válida."
        )

    def test_duplicate_email_rejected_case_insensitive(self):
        make_company(created_by=self.user)
        response = self._post(name="Otra Empresa", rut="11.111.111-1")
        self.assertFormError(
            response.context["form"],
            "email",
            "Ya existe una empresa con este correo.",
        )

    def test_email_normalized_to_lowercase(self):
        response = self._post(email="CONTACTO@ENERGIASOLAR.CL")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            Company.objects.get().email, "contacto@energiasolar.cl"
        )

    def test_rut_normalized_to_dotted_format(self):
        response = self._post(rut="12345678-5")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Company.objects.get().rut, "12.345.678-5")


class CompanyCreateViewTests(TestCase):
    def test_create_requires_login(self):
        response = self.client.get(reverse("companies:create"))
        self.assertRedirects(
            response, f"{reverse('login')}?next={reverse('companies:create')}"
        )

    def test_staff_cannot_create_get(self):
        staff = User.objects.create_user(
            username="staff",
            password="clave-segura-123",
            is_staff=True,
        )
        self.client.force_login(staff)
        response = self.client.get(reverse("companies:create"))
        self.assertEqual(response.status_code, 403)

    def test_staff_cannot_create_post(self):
        staff = User.objects.create_user(
            username="staff",
            password="clave-segura-123",
            is_staff=True,
        )
        self.client.force_login(staff)
        response = self.client.post(
            reverse("companies:create"),
            {
                "name": "Staff SpA",
                "rut": VALID_RUT,
                "email": "staff@example.com",
            },
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Company.objects.count(), 0)

    def test_valid_create_links_user_and_redirects_to_detail(self):
        user = make_user()
        self.client.force_login(user)
        response = self.client.post(
            reverse("companies:create"),
            {
                "name": "Energía Solar SpA",
                "alias": "ES",
                "address": "Av. Siempre Viva 123",
                "rut": VALID_RUT,
                "email": "contacto@energiasolar.cl",
            },
        )
        company = Company.objects.get()
        self.assertRedirects(
            response,
            reverse("companies:detail", kwargs={"uuid": company.uuid}),
        )
        self.assertEqual(company.created_by, user)


class CompanyDetailViewTests(TestCase):
    def test_detail_requires_login(self):
        company = make_company(created_by=make_user())
        response = self.client.get(
            reverse("companies:detail", kwargs={"uuid": company.uuid})
        )
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('companies:detail', kwargs={'uuid': company.uuid})}",
        )

    def test_detail_uses_uuid_url(self):
        company = make_company(created_by=make_user())
        url = reverse("companies:detail", kwargs={"uuid": company.uuid})
        self.assertEqual(url, f"/companies/{company.uuid}/")
        self.assertNotEqual(url.rsplit("/")[-2], "id")

    def test_detail_accessible_to_owner(self):
        user = make_user()
        company = make_company(created_by=user)
        self.client.force_login(user)
        response = self.client.get(
            reverse("companies:detail", kwargs={"uuid": company.uuid})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, company.name)

    def test_detail_not_accessible_to_other_user(self):
        owner = make_user("owner")
        company = make_company(created_by=owner)
        self.client.force_login(make_user("other"))
        response = self.client.get(
            reverse("companies:detail", kwargs={"uuid": company.uuid})
        )
        self.assertEqual(response.status_code, 404)

    def test_detail_not_accessible_for_deleted_company(self):
        user = make_user()
        company = make_company(created_by=user)
        company.delete()
        self.client.force_login(user)
        response = self.client.get(
            reverse("companies:detail", kwargs={"uuid": company.uuid})
        )
        self.assertEqual(response.status_code, 404)


class CompanyUpdateViewTests(TestCase):
    def _update_url(self, company):
        return reverse("companies:update", kwargs={"uuid": company.uuid})

    def _data(self, **overrides):
        data = {
            "name": "Energía Solar Actualizada SpA",
            "alias": "ESA",
            "rut": VALID_RUT,
            "email": "contacto@energiasolar.cl",
        }
        data.update(overrides)
        return data

    def test_update_requires_login(self):
        company = make_company(created_by=make_user())
        response = self.client.get(self._update_url(company))
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={self._update_url(company)}",
        )

    def test_staff_cannot_update(self):
        staff = User.objects.create_user(
            username="staff",
            password="clave-segura-123",
            is_staff=True,
        )
        company = make_company(created_by=staff)
        self.client.force_login(staff)
        response = self.client.post(self._update_url(company), self._data())
        self.assertEqual(response.status_code, 403)
        company.refresh_from_db()
        self.assertEqual(company.name, "Energía Solar SpA")

    def test_owner_can_update_and_redirects_to_detail(self):
        user = make_user()
        company = make_company(created_by=user)
        self.client.force_login(user)
        response = self.client.post(self._update_url(company), self._data())
        self.assertRedirects(
            response,
            reverse("companies:detail", kwargs={"uuid": company.uuid}),
        )
        company.refresh_from_db()
        self.assertEqual(company.name, "Energía Solar Actualizada SpA")
        self.assertEqual(company.alias, "ESA")

    def test_cannot_update_other_users_company(self):
        owner = make_user("owner")
        company = make_company(created_by=owner)
        self.client.force_login(make_user("other"))
        response = self.client.post(self._update_url(company), self._data())
        self.assertEqual(response.status_code, 404)
        company.refresh_from_db()
        self.assertEqual(company.name, "Energía Solar SpA")

    def test_cannot_update_deleted_company(self):
        user = make_user()
        company = make_company(created_by=user)
        company.delete()
        self.client.force_login(user)
        response = self.client.post(self._update_url(company), self._data())
        self.assertEqual(response.status_code, 404)


class CompanyDeleteViewTests(TestCase):
    def _delete_url(self, company):
        return reverse("companies:delete", kwargs={"uuid": company.uuid})

    def test_delete_requires_login(self):
        company = make_company(created_by=make_user())
        response = self.client.post(self._delete_url(company))
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={self._delete_url(company)}",
        )

    def test_staff_cannot_delete(self):
        staff = User.objects.create_user(
            username="staff",
            password="clave-segura-123",
            is_staff=True,
        )
        company = make_company(created_by=staff)
        self.client.force_login(staff)
        response = self.client.post(self._delete_url(company))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Company.objects.count(), 1)

    def test_owner_delete_is_soft_and_redirects_to_home(self):
        user = make_user()
        company = make_company(created_by=user)
        self.client.force_login(user)
        response = self.client.post(self._delete_url(company))
        self.assertRedirects(response, reverse("home"))
        company.refresh_from_db()
        self.assertIsNotNone(company.deleted_at)
        self.assertEqual(Company.objects.count(), 0)
        self.assertEqual(Company.objects.all_with_deleted().count(), 1)

    def test_cannot_delete_other_users_company(self):
        owner = make_user("owner")
        company = make_company(created_by=owner)
        self.client.force_login(make_user("other"))
        response = self.client.post(self._delete_url(company))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Company.objects.all_with_deleted().count(), 1)

    def test_get_does_not_delete(self):
        user = make_user()
        company = make_company(created_by=user)
        self.client.force_login(user)
        response = self.client.get(self._delete_url(company))
        self.assertEqual(response.status_code, 405)
        self.assertEqual(Company.objects.count(), 1)


class CompanyModalFormTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.client.force_login(self.user)

    def _valid_data(self, **overrides):
        data = {
            "name": "Energía Solar SpA",
            "alias": "ES",
            "address": "Av. Siempre Viva 123",
            "rut": VALID_RUT,
            "email": "contacto@energiasolar.cl",
            "form": "modal",
        }
        data.update(overrides)
        return data

    def test_create_modal_returns_partial(self):
        response = self.client.get(
            reverse("companies:create"), {"form": "modal"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "companies/_form.html")
        self.assertNotContains(response, "<html")
        self.assertContains(response, "<form")

    def test_create_modal_success_returns_json(self):
        response = self.client.post(
            reverse("companies:create"), self._valid_data()
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"success": True})
        company = Company.objects.get()
        self.assertEqual(company.created_by, self.user)

    def test_create_modal_invalid_renders_partial_with_errors(self):
        response = self.client.post(
            reverse("companies:create"),
            self._valid_data(name=""),
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "companies/_form.html")
        self.assertContains(response, "Este campo es obligatorio.")

    def test_update_modal_returns_partial_with_action(self):
        company = make_company(created_by=self.user)
        response = self.client.get(
            reverse("companies:update", kwargs={"uuid": company.uuid}),
            {"form": "modal"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "companies/_form.html")
        self.assertContains(
            response,
            reverse("companies:update", kwargs={"uuid": company.uuid}),
        )

    def test_update_modal_success_returns_json(self):
        company = make_company(created_by=self.user)
        response = self.client.post(
            reverse("companies:update", kwargs={"uuid": company.uuid}),
            self._valid_data(name="Energía Solar Actualizada SpA"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"success": True})
        company.refresh_from_db()
        self.assertEqual(company.name, "Energía Solar Actualizada SpA")

    def test_update_modal_invalid_renders_partial_with_errors(self):
        company = make_company(created_by=self.user)
        response = self.client.post(
            reverse("companies:update", kwargs={"uuid": company.uuid}),
            self._valid_data(rut="76.123.456-7"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "companies/_form.html")
        self.assertContains(response, "El RUT ingresado no es válido.")

    def test_modal_staff_forbidden(self):
        staff = User.objects.create_user(
            username="staff",
            password="clave-segura-123",
            is_staff=True,
        )
        self.client.force_login(staff)
        response = self.client.get(
            reverse("companies:create"), {"form": "modal"}
        )
        self.assertEqual(response.status_code, 403)

    def test_update_modal_other_user_404(self):
        owner = make_user("owner")
        company = make_company(created_by=owner)
        response = self.client.post(
            reverse("companies:update", kwargs={"uuid": company.uuid}),
            self._valid_data(),
        )
        self.assertEqual(response.status_code, 404)