# Generated by Django 5.0.7 on 2024-11-09 23:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estudiantes', '0006_solicitudbajaprovisoria'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificacion',
            name='tipo_evento',
            field=models.CharField(default=0, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='notificacion',
            name='visto',
            field=models.BooleanField(default=False),
        ),
    ]
