import uuid

from django.db import models
from django.utils import timezone

from companies.models import Company

from .catalog import COMMUNE_CHOICES, PaymentMethod


class CustomerQuerySet(models.QuerySet):
    def alive(self):
        return self.filter(deleted_at__isnull=True)

    def dead(self):
        return self.filter(deleted_at__isnull=False)

    def delete(self, hard=False, **kwargs):
        if hard:
            return super().delete(**kwargs)
        return self.update(deleted_at=timezone.now())

    def hard_delete(self, **kwargs):
        return self.delete(hard=True, **kwargs)


class CustomerManager(models.Manager):
    def get_queryset(self):
        return CustomerQuerySet(self.model, using=self._db).alive()

    def all_with_deleted(self):
        return CustomerQuerySet(self.model, using=self._db)

    def dead(self):
        return self.all_with_deleted().dead()


class Customer(models.Model):
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name="customers",
    )
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    commune = models.CharField(
        max_length=100,
        choices=COMMUNE_CHOICES,
    )
    payment_method = models.CharField(
        max_length=30,
        choices=PaymentMethod.choices,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = CustomerManager()

    def delete(self, using=None, keep_parents=False):
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at", "updated_at"])

    def hard_delete(self, using=None, keep_parents=False):
        return super().delete(using=using, keep_parents=keep_parents)

    def __str__(self):
        return self.name
