import os
from pathlib import Path
import subprocess
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app_config.settings")

import django

django.setup()

import pytest
from playwright.sync_api import sync_playwright

BASE_URL = os.getenv("E2E_BASE_URL", "http://localhost:8000")
CAPTURAS = Path("/workspace/.pytest_cache/capturas")
PROJECT_DIR = Path(__file__).resolve().parents[2]

USERNAME = "e2e_modal"
PASSWORD = "clave-segura-123"

_SEED_CODE = """
from django.contrib.auth.models import User
from companies.models import Company
Company.objects.filter(name__startswith='E2E ').hard_delete()
User.objects.filter(username='e2e_modal').delete()
User.objects.create_user(username='e2e_modal', password='clave-segura-123')
print('seed ok')
"""


def _seed_dev_db():
    subprocess.run(
        [sys.executable, "manage.py", "shell", "-c", _SEED_CODE],
        cwd=PROJECT_DIR,
        check=True,
        capture_output=True,
    )


def _login(page):
    page.goto(f"{BASE_URL}/login/")
    page.fill("#id_username", USERNAME)
    page.fill("#id_password", PASSWORD)
    page.click("form button[type='submit']")
    page.wait_for_url(f"{BASE_URL}/")


def _open_create_modal(page):
    page.click("button[data-modal-open][data-modal-title='Crear empresa']")
    page.wait_for_selector("#appModalBody form")


@pytest.mark.e2e
def test_company_create_modal():
    CAPTURAS.mkdir(parents=True, exist_ok=True)
    _seed_dev_db()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        _login(page)

        _open_create_modal(page)
        page.fill("#id_name", "E2E Empresa Solar")
        page.fill("#id_alias", "E2E")
        page.fill("#id_address", "Av. E2E 123")
        page.fill("#id_rut", "22.222.222-2")
        page.fill("#id_email", "e2e.empresa@example.com")
        page.screenshot(path=str(CAPTURAS / "modal_formulario.png"))

        page.click("#appModalBody form button[type='submit']")
        page.wait_for_selector("table tbody tr:has-text('E2E Empresa Solar')")

        page.wait_for_selector("#appModal", state="hidden")
        page.wait_for_selector(".alert:has-text('Empresa creada exitosamente.')")
        page.screenshot(path=str(CAPTURAS / "modal_creada.png"))
        browser.close()


@pytest.mark.e2e
def test_company_update_modal():
    CAPTURAS.mkdir(parents=True, exist_ok=True)
    _seed_dev_db()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        _login(page)

        _open_create_modal(page)
        page.fill("#id_name", "E2E Empresa Solar")
        page.fill("#id_alias", "E2E")
        page.fill("#id_address", "Av. E2E 123")
        page.fill("#id_rut", "22.222.222-2")
        page.fill("#id_email", "e2e.empresa@example.com")
        page.click("#appModalBody form button[type='submit']")
        page.wait_for_selector("table tbody tr:has-text('E2E Empresa Solar')")

        page.click("button[data-modal-open][data-modal-title='Editar E2E Empresa Solar']")
        page.wait_for_selector("#appModalBody form")
        page.fill("#id_alias", "E2E Actualizada")
        page.screenshot(path=str(CAPTURAS / "modal_editar.png"))
        page.click("#appModalBody form button[type='submit']")

        page.wait_for_selector("table tbody tr:has-text('E2E Actualizada')")
        page.wait_for_selector(".alert:has-text('Empresa actualizada exitosamente.')")
        page.screenshot(path=str(CAPTURAS / "modal_editada.png"))
        browser.close()