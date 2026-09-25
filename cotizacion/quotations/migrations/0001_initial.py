import django.core.validators
import django.db.models.deletion
import uuid
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('companies', '0001_initial'),
        ('customers', '0002_alter_customer_commune'),
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Quotation',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('status', models.CharField(choices=[('draft', 'Borrador'), ('issued', 'Emitida'), ('accepted', 'Aceptada'), ('rejected', 'Rechazada')], default='draft', max_length=20)),
                ('notes', models.TextField(blank=True)),
                ('total', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=14)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='quotations', to='companies.company')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='quotations', to='customers.customer', to_field='uuid')),
            ],
        ),
        migrations.CreateModel(
            name='QuotationItem',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('product_name', models.CharField(max_length=200)),
                ('product_sku', models.CharField(blank=True, max_length=100)),
                ('unit', models.CharField(choices=[('unit', 'Unidad'), ('meter', 'Metro'), ('square_meter', 'Metro cuadrado'), ('hour', 'Hora'), ('day', 'Día'), ('service', 'Servicio')], max_length=20)),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=12)),
                ('quantity', models.DecimalField(decimal_places=3, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.001'))])),
                ('subtotal', models.DecimalField(decimal_places=2, max_digits=14)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='quotation_items', to='products.product', to_field='uuid')),
                ('quotation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='quotations.quotation')),
            ],
        ),
    ]
