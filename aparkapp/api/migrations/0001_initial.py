# Generated by Django 4.0.3 on 2022-03-13 09:56

from django.conf import settings
import django.contrib.auth.models
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateTimeField()),
                ('wait_time', models.IntegerField()),
                ('price', models.FloatField(validators=[django.core.validators.MinValueValidator(0.5), django.core.validators.MaxValueValidator(10)])),
                ('allow_wait', models.BooleanField(default=False)),
                ('location', models.CharField(max_length=1024)),
                ('zone', models.CharField(choices=[('Zona libre', 'La plaza está situada en una zona libre'), ('Zona Azul', 'La plaza está situada en zona azul'), ('Zona Verde', 'La plaza está situada en zona verde'), ('Zona Roja', 'La plaza está situada en zona roja'), ('Zona Naranja', 'La plaza está situada en zona naranja'), ('Zona MAR', 'La plaza está situada en zona de muy alta rotación')], default='Zona libre', max_length=256)),
                ('limited_mobility', models.BooleanField(default=False)),
                ('status', models.CharField(choices=[('Initial', 'Estado inicial'), ('Arrival', 'Estado llegada'), ('Departure', 'Estado salida')], default='Initial', max_length=256)),
                ('observation', models.CharField(max_length=500)),
                ('rated', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('phone', models.CharField(max_length=12)),
                ('birthdate', models.DateField()),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Vehicle',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('brand', models.CharField(max_length=200)),
                ('model', models.CharField(max_length=400)),
                ('license_plate', models.CharField(max_length=10)),
                ('color', models.CharField(max_length=100)),
                ('type', models.CharField(choices=[('Segmento A', 'El vehículo pertenece al segmento A'), ('Segmento B', 'El vehículo pertenece al segmento B'), ('Segmento C', 'El vehículo pertenece al segmento C'), ('Segmento D', 'El vehículo pertenece al segmento D'), ('Segmento E', 'El vehículo pertenece al segmento E')], default='Segmento A', max_length=256)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.user')),
            ],
        ),
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateTimeField()),
                ('n_extend', models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(3)])),
                ('cancelled', models.BooleanField(default=False)),
                ('rated', models.BooleanField(default=False)),
                ('announcement', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='api.announcement')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.user')),
            ],
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('rate', models.IntegerField(choices=[(1, 'Muy mala'), (2, 'Mala'), (3, 'Regular'), (4, 'Buena'), (5, 'Muy Buena')], validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)])),
                ('comment', models.CharField(max_length=500)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.user')),
            ],
        ),
        migrations.AddField(
            model_name='announcement',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.user'),
        ),
        migrations.AddField(
            model_name='announcement',
            name='vehicle',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.vehicle'),
        ),
    ]
