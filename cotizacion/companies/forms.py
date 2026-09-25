from django import forms
from django.core.exceptions import ValidationError

from .models import Company
from .validators import validate_rut

FORM_CONTROL = "form-control"


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ("name", "alias", "address", "rut", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = FORM_CONTROL

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        queryset = Company.objects.filter(email__iexact=email)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise ValidationError("Ya existe una compañía con este correo.")
        return email

    def clean_rut(self):
        rut = validate_rut(self.cleaned_data["rut"])
        queryset = Company.objects.filter(rut=rut)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise ValidationError("Ya existe una compañía con este RUT.")
        return rut