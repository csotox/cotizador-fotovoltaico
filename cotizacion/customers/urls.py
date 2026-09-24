from django.urls import path

from . import views

app_name = "customers"

urlpatterns = [
    path("", views.CustomerListView.as_view(), name="list"),
    path("nuevo/", views.CustomerCreateView.as_view(), name="create"),
    path("<uuid:uuid>/editar/", views.CustomerUpdateView.as_view(), name="update"),
    path("<uuid:uuid>/", views.CustomerDetailView.as_view(), name="detail"),
    path("<uuid:uuid>/eliminar/", views.CustomerDeleteView.as_view(), name="delete"),
]
