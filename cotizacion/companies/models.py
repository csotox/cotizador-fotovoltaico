import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class CompanyQuerySet(models.QuerySet):
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


class CompanyManager(models.Manager):
    def get_queryset(self):
        return CompanyQuerySet(self.model, using=self._db).alive()

    def all_with_deleted(self):
        return CompanyQuerySet(self.model, using=self._db)

    def dead(self):
        return self.all_with_deleted().dead()


class Company(models.Model):
    id = models.BigAutoField(primary_key=True)

    uuid = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )

    name = models.CharField(max_length=200)
    alias = models.CharField(max_length=120, blank=True)
    address = models.CharField(max_length=255, blank=True)
    rut = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="companies",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = CompanyManager()

    def delete(self, using=None, keep_parents=False):
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at", "updated_at"])

    def hard_delete(self, using=None, keep_parents=False):
        return super().delete(using=using, keep_parents=keep_parents)

    def __str__(self):
        return self.name