# Generated by Django 5.0.7 on 2024-10-04 05:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estudiantes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cuota',
            name='estado',
            field=models.CharField(choices=[('pendiente', 'Pendiente'), ('pagada', 'Pagada'), ('informada', 'Informada'), ('vencida', 'Vencida')], default='pendiente', max_length=10),
        ),
    ]
