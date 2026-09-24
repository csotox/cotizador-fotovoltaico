from pathlib import Path

import pytest
from django.contrib.auth.models import User
from playwright.sync_api import sync_playwright

from companies.models import Company

CAPTURAS = Path("/workspace/.pytest_cache/capturas")

USERNAME = "e2e_modal"
PASSWORD = "clave-segura-123"
COMPANY_NAME = "E2E Empresa Solar"
RUT = "22.222.222-2"
EMAIL = "e2e.empresa@example.com"


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


def _fill_company_form(page):
    page.fill("#id_name", COMPANY_NAME)
    page.fill("#id_alias", "E2E")
    page.fill("#id_address", "Av. E2E 123")
    page.fill("#id_rut", RUT)
    page.fill("#id_email", EMAIL)


@pytest.mark.e2e
@pytest.mark.django_db(transaction=True)
def test_company_create_modal(live_server):
    CAPTURAS.mkdir(parents=True, exist_ok=True)
    _seed()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        _login(page, live_server.url)
        page.click("button[data-modal-open][data-modal-title='Crear empresa']")
        page.wait_for_selector("#appModalBody form")

        _fill_company_form(page)
        page.screenshot(path=str(CAPTURAS / "modal_formulario.png"))

        page.click("#appModalBody form button[type='submit']")
        page.wait_for_selector(f"table tbody tr:has-text('{COMPANY_NAME}')")
        page.wait_for_selector("#appModal", state="hidden")
        page.wait_for_selector(".alert:has-text('Empresa creada exitosamente.')")
        page.screenshot(path=str(CAPTURAS / "modal_creada.png"))

        browser.close()

    company = Company.objects.get(name=COMPANY_NAME)
    assert company.deleted_at is None


@pytest.mark.e2e
@pytest.mark.django_db(transaction=True)
def test_company_update_modal(live_server):
    CAPTURAS.mkdir(parents=True, exist_ok=True)
    _seed()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        _login(page, live_server.url)
        page.click("button[data-modal-open][data-modal-title='Crear empresa']")
        page.wait_for_selector("#appModalBody form")

        _fill_company_form(page)
        page.click("#appModalBody form button[type='submit']")
        page.wait_for_selector(f"table tbody tr:has-text('{COMPANY_NAME}')")

        page.click(f"button[data-modal-open][data-modal-title='Editar {COMPANY_NAME}']")
        page.wait_for_selector("#appModalBody form")
        page.fill("#id_alias", "E2E Actualizada")
        page.screenshot(path=str(CAPTURAS / "modal_editar.png"))
        page.click("#appModalBody form button[type='submit']")

        page.wait_for_selector("table tbody tr:has-text('E2E Actualizada')")
        page.wait_for_selector(".alert:has-text('Empresa actualizada exitosamente.')")
        page.screenshot(path=str(CAPTURAS / "modal_editada.png"))

        browser.close()

    company = Company.objects.get(name=COMPANY_NAME)
    assert company.alias == "E2E Actualizada"