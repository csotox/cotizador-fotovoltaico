from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import resolve, reverse


class SignUpViewTests(TestCase):
    def test_signup_page_renders(self):
        response = self.client.get(reverse("signup"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Registrarse")

    def test_signup_redirects_to_login_url(self):
        self.assertEqual(resolve(reverse("signup")).route, "registro/")

    def test_valid_signup_creates_user_and_redirects_to_login(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "vendedor",
                "email": "vendedor@example.com",
                "password1": "clave-segura-123",
                "password2": "clave-segura-123",
            },
        )
        self.assertRedirects(response, reverse("login"))
        user = User.objects.get(username="vendedor")
        self.assertEqual(user.email, "vendedor@example.com")
        self.assertTrue(user.is_active)

    def test_duplicate_username_rejected(self):
        User.objects.create_user(username="vendedor", password="clave-segura-123")
        response = self.client.post(
            reverse("signup"),
            {
                "username": "vendedor",
                "email": "otro@example.com",
                "password1": "clave-segura-123",
                "password2": "clave-segura-123",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"],
            "username",
            "A user with that username already exists.",
        )

    def test_duplicate_email_rejected(self):
        User.objects.create_user(
            username="otro",
            email="vendedor@example.com",
            password="clave-segura-123",
        )
        response = self.client.post(
            reverse("signup"),
            {
                "username": "vendedor",
                "email": "VENDEDOR@example.com",
                "password1": "clave-segura-123",
                "password2": "clave-segura-123",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"],
            "email",
            "Ya existe un usuario registrado con este correo.",
        )

    def test_email_normalized_to_lowercase(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "vendedor",
                "email": "Vendedor@Example.com",
                "password1": "clave-segura-123",
                "password2": "clave-segura-123",
            },
        )
        self.assertRedirects(response, reverse("login"))
        self.assertEqual(User.objects.get(username="vendedor").email, "vendedor@example.com")

    def test_payload_without_email_rejected(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "vendedor",
                "email": "",
                "password1": "clave-segura-123",
                "password2": "clave-segura-123",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context["form"], "email", "This field is required.")

    def test_password_mismatch_rejected(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "vendedor",
                "email": "vendedor@example.com",
                "password1": "clave-segura-123",
                "password2": "clave-segura-456",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"],
            "password2",
            "The two password fields didn’t match.",
        )

    def test_common_password_rejected(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "vendedor",
                "email": "vendedor@example.com",
                "password1": "password",
                "password2": "password",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="vendedor").exists())

    def test_numeric_password_rejected(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "vendedor",
                "email": "vendedor@example.com",
                "password1": "12345678",
                "password2": "12345678",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="vendedor").exists())

    def test_short_password_rejected(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "vendedor",
                "email": "vendedor@example.com",
                "password1": "abc",
                "password2": "abc",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="vendedor").exists())


class LoginTests(TestCase):
    def test_authenticate_after_signup(self):
        self.client.post(
            reverse("signup"),
            {
                "username": "vendedor",
                "email": "vendedor@example.com",
                "password1": "clave-segura-123",
                "password2": "clave-segura-123",
            },
        )
        response = self.client.post(
            reverse("login"),
            {"username": "vendedor", "password": "clave-segura-123"},
        )
        self.assertRedirects(response, reverse("home"))

    def test_login_does_not_reveal_existence(self):
        response = self.client.post(
            reverse("login"),
            {"username": "no-existe", "password": "clave-segura-123"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"],
            None,
            "Please enter a correct username and password. Note that both fields may be case-sensitive.",
        )


class HomeViewTests(TestCase):
    def test_home_requires_login(self):
        response = self.client.get(reverse("home"))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('home')}")

    def test_home_accessible_authenticated(self):
        user = User.objects.create_user(username="vendedor", password="clave-segura-123")
        self.client.force_login(user)
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bienvenido")