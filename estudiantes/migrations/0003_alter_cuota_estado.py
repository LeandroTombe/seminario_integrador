# Generated by Django 5.0.7 on 2024-10-07 20:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estudiantes', '0002_alter_cuota_estado'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cuota',
            name='estado',
            field=models.CharField(choices=[('pendiente', 'Pendiente'), ('pagada', 'Pagada'), ('informada', 'Informada'), ('vencida', 'Vencida')], default='Pendiente', max_length=10),
        ),
    ]
