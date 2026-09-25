from pathlib import Path

import pytest
from django.contrib.auth.models import User
from playwright.sync_api import sync_playwright

from companies.models import Company
from customers.models import Customer

CAPTURAS = Path("/workspace/.pytest_cache/capturas")
USERNAME = "e2e_clientes"
PASSWORD = "clave-segura-123"
COMPANY_NAME = "E2E Compañía Solar"
CUSTOMER_NAME = "Cliente E2E Solar"
RUT = "33.333.333-3"
COMPANY_EMAIL = "e2e.compania@example.com"
CUSTOMER_EMAIL = "e2e.cliente@example.com"


def _seed():
    User.objects.filter(username=USERNAME).delete()
    User.objects.create_user(username=USERNAME, password=PASSWORD)
    Company.objects.filter(name__startswith="E2E ").hard_delete()


def _login(page, base_url):
    page.goto(f"{base_url}/login/")
    page.fill("#id_username", USERNAME)
    page.fill("#id_password", PASSWORD)
    page.click("form button[type='submit']")
    page.wait_for_url(f"{base_url}/")


def _fill_customer_form(page):
    page.fill("#id_name", CUSTOMER_NAME)
    page.fill("#id_address", "Av. Cliente 123")
    page.fill("#id_email", CUSTOMER_EMAIL)
    page.fill("#id_phone", "+56912345678")
    page.select_option("#id_commune", "Santiago")
    page.select_option("#id_payment_method", "bank_transfer")


@pytest.mark.e2e
@pytest.mark.django_db(transaction=True)
def test_customer_create_modal(live_server):
    CAPTURAS.mkdir(parents=True, exist_ok=True)
    _seed()
    user = User.objects.get(username=USERNAME)
    Company.objects.create(
        created_by=user,
        name=COMPANY_NAME,
        alias="E2E",
        address="Av. Compañía 123",
        rut=RUT,
        email=COMPANY_EMAIL,
    )

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        _login(page, live_server.url)
        page.goto(f"{live_server.url}/customers/")
        page.click("button[data-modal-open][data-modal-title='Crear cliente destinatario']")
        page.wait_for_selector("#appModalBody form")
        _fill_customer_form(page)
        page.screenshot(path=str(CAPTURAS / "cliente_modal.png"))
        page.click("#appModalBody form button[type='submit']")
        page.wait_for_selector(f"table tbody tr:has-text('{CUSTOMER_NAME}')")
        page.wait_for_selector("#appModal", state="hidden")
        page.screenshot(path=str(CAPTURAS / "cliente_creado.png"))
        browser.close()

    customer = Customer.objects.get(name=CUSTOMER_NAME)
    assert customer.company.name == COMPANY_NAME
    assert customer.email == CUSTOMER_EMAIL
