from django.urls import path

from . import views

app_name = "products"

urlpatterns = [
    path("", views.ProductListView.as_view(), name="list"),
    path("nuevo/", views.ProductCreateView.as_view(), name="create"),
    path("<uuid:uuid>/editar/", views.ProductUpdateView.as_view(), name="update"),
    path("<uuid:uuid>/", views.ProductDetailView.as_view(), name="detail"),
    path("<uuid:uuid>/eliminar/", views.ProductDeleteView.as_view(), name="delete"),
]
