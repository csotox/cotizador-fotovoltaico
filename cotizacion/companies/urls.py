from django.urls import path

from . import views

app_name = "companies"

urlpatterns = [
    path("", views.CompanyListView.as_view(), name="list"),
    path("nueva/", views.CompanyCreateView.as_view(), name="create"),
    path("<uuid:uuid>/", views.CompanyDetailView.as_view(), name="detail"),
]