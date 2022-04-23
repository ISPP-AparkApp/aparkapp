# Generated by Django 4.0.3 on 2022-04-23 12:42

from decimal import Decimal
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import djmoney.models.fields
import djmoney.models.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateTimeField()),
                ('wait_time', models.PositiveSmallIntegerField(default=0)),
                ('price', models.FloatField(validators=[django.core.validators.MinValueValidator(0.5), django.core.validators.MaxValueValidator(10)])),
                ('allow_wait', models.BooleanField(default=False)),
                ('location', models.CharField(blank=True, max_length=1024)),
                ('longitude', models.FloatField(validators=[django.core.validators.MinValueValidator(-180.0), django.core.validators.MaxValueValidator(180.0)])),
                ('latitude', models.FloatField(validators=[django.core.validators.MinValueValidator(-90.0), django.core.validators.MaxValueValidator(90.0)])),
                ('zone', models.CharField(choices=[('Zona libre', 'La plaza está situada en una zona libre'), ('Zona Azul', 'La plaza está situada en zona azul'), ('Zona Verde', 'La plaza está situada en zona verde'), ('Zona Roja', 'La plaza está situada en zona roja'), ('Zona Naranja', 'La plaza está situada en zona naranja'), ('Zona MAR', 'La plaza está situada en zona de muy alta rotación')], default='Zona libre', max_length=256)),
                ('limited_mobility', models.BooleanField(default=False)),
                ('status', models.CharField(choices=[('Initial', 'Estado inicial'), ('Delay', 'Estado retraso'), ('AcceptDelay', 'Estado aceptar retraso'), ('DenyDelay', 'Estado rechazar retraso'), ('Arrival', 'Estado llegada'), ('Departure', 'Estado salida')], default='Initial', max_length=256)),
                ('observation', models.CharField(default='Sin comentarios.', max_length=500)),
                ('rated', models.BooleanField(default=False)),
                ('cancelled', models.BooleanField(default=False)),
                ('announcement', models.BooleanField(choices=[(True, 'Esto es un anuncio')], default=True)),
                ('n_extend', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(3)])),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Vehicle',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('brand', models.CharField(max_length=200)),
                ('model', models.CharField(max_length=400)),
                ('license_plate', models.CharField(max_length=10, unique=True)),
                ('color', models.CharField(max_length=100)),
                ('type', models.CharField(choices=[('Pequeño', 'El vehículo es pequeño'), ('Mediano', 'El vehículo es mediano'), ('Grande', 'El vehículo es grande')], default='Pequeño', max_length=256)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vehicles', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateTimeField()),
                ('cancelled', models.BooleanField(default=False)),
                ('rated', models.BooleanField(default=False)),
                ('announcement', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.announcement')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('rate', models.IntegerField(choices=[(1, 'Muy mala'), (2, 'Mala'), (3, 'Regular'), (4, 'Buena'), (5, 'Muy Buena')], validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)])),
                ('comment', models.CharField(max_length=500)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('phone', models.CharField(max_length=12)),
                ('birthdate', models.DateField()),
                ('balance_currency', djmoney.models.fields.CurrencyField(choices=[('GBP', 'British Pound'), ('CAD', 'Canadian Dollar'), ('EUR', 'Euro'), ('JPY', 'Japanese Yen'), ('CHF', 'Swiss Franc'), ('USD', 'US Dollar')], default='EUR', editable=False, max_length=3)),
                ('balance', djmoney.models.fields.MoneyField(decimal_places=2, default=Decimal('0.0'), default_currency='EUR', max_digits=6, validators=[djmoney.models.validators.MinMoneyValidator(0)])),
                ('is_banned', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='announcement',
            name='vehicle',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.vehicle'),
        ),
    ]
