import pytest
from django.conf import settings


@pytest.fixture(autouse=True)
def _guard_test_database():
    name = settings.DATABASES["default"]["NAME"]
    if not name.startswith("test_"):
        pytest.fail(
            f"Los tests no deben ejecutarse sobre la base de datos de desarrollo: '{name}'"
        )