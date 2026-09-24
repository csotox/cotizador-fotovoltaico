from django.db import models


COMMUNE_CHOICES = (
    ("Arica", "Arica"),
    ("Iquique", "Iquique"),
    ("Antofagasta", "Antofagasta"),
    ("Calama", "Calama"),
    ("Copiapó", "Copiapó"),
    ("La Serena", "La Serena"),
    ("Coquimbo", "Coquimbo"),
    ("Ovalle", "Ovalle"),
    ("Valparaíso", "Valparaíso"),
    ("Viña del Mar", "Viña del Mar"),
    ("Quilpué", "Quilpué"),
    ("San Antonio", "San Antonio"),
    ("Santiago", "Santiago"),
    ("Puente Alto", "Puente Alto"),
    ("Maipú", "Maipú"),
    ("La Florida", "La Florida"),
    ("Las Condes", "Las Condes"),
    ("Ñuñoa", "Ñuñoa"),
    ("Peñalolén", "Peñalolén"),
    ("Conchalí", "Conchalí"),
    ("Quilicura", "Quilicura"),
    ("Lampa", "Lampa"),
    ("Colina", "Colina"),
    ("Buin", "Buin"),
    ("Pudahuel", "Pudahuel"),
    ("Talagante", "Talagante"),
    ("Machalí", "Machalí"),
    ("Rancagua", "Rancagua"),
    ("San Fernando", "San Fernando"),
    ("Curicó", "Curicó"),
    ("Talca", "Talca"),
    ("Linares", "Linares"),
    ("Cauquenes", "Cauquenes"),
    ("Concepción", "Concepción"),
    ("Talcahuano", "Talcahuano"),
    ("Chillán", "Chillán"),
    ("Los Ángeles", "Los Ángeles"),
    ("Temuco", "Temuco"),
    ("Villarrica", "Villarrica"),
    ("Valdivia", "Valdivia"),
    ("Osorno", "Osorno"),
    ("Puerto Montt", "Puerto Montt"),
    ("Castro", "Castro"),
    ("Coyhaique", "Coyhaique"),
    ("Punta Arenas", "Punta Arenas"),
)


class PaymentMethod(models.TextChoices):
    CASH = "cash", "Efectivo"
    BANK_TRANSFER = "bank_transfer", "Transferencia bancaria"
    CHECK = "check", "Cheque"
    DEBIT_CARD = "debit_card", "Tarjeta de débito"
    CREDIT_CARD = "credit_card", "Tarjeta de crédito"
    PROMISSORY_NOTES = "promissory_notes", "Letras de cambio"
