# Generated by Django 4.0.2 on 2022-03-12 11:01

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_announcement_rating_reservation_user_vehicle_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='announcement',
            name='vehicle',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='api.vehicle'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='rating',
            name='user',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='api.user'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='reservation',
            name='announcement',
            field=models.OneToOneField(default='', on_delete=django.db.models.deletion.CASCADE, to='api.announcement'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='reservation',
            name='user',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='api.user'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='vehicle',
            name='user',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='api.user'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='announcement',
            name='price',
            field=models.FloatField(validators=[django.core.validators.MinValueValidator(0.5), django.core.validators.MaxValueValidator(10)]),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='n_extend',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(3)]),
        ),
    ]
