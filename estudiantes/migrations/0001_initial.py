# Generated by Django 5.0.7 on 2024-10-04 04:44

import django.db.models.deletion
import estudiantes.validators
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Coordinador',
            fields=[
                ('nombre', models.CharField(max_length=255)),
                ('apellido', models.CharField(max_length=255)),
                ('telefono', models.IntegerField()),
                ('email', models.EmailField(max_length=254)),
                ('dni', models.IntegerField()),
                ('codCoor', models.IntegerField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Materia',
            fields=[
                ('codigo_materia', models.IntegerField(auto_created=True, primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=50, validators=[estudiantes.validators.validar_nombre])),
            ],
        ),
        migrations.CreateModel(
            name='ParametrosCompromiso',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('año', models.IntegerField()),
                ('cuatrimestre', models.IntegerField()),
                ('compromiso_contenido', models.FileField(blank=True, null=True, upload_to='compromiso/')),
                ('importe_matricula', models.DecimalField(decimal_places=2, max_digits=10)),
                ('importe_reducido', models.DecimalField(decimal_places=2, max_digits=10)),
                ('importe_completo', models.DecimalField(decimal_places=2, max_digits=10)),
                ('importe_pri_venc_comp', models.DecimalField(decimal_places=2, max_digits=10)),
                ('importe_pri_venc_red', models.DecimalField(decimal_places=2, max_digits=10)),
                ('importe_seg_venc_comp', models.DecimalField(decimal_places=2, max_digits=10)),
                ('importe_seg_venc_red', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='Alumno',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('legajo', models.IntegerField()),
                ('nombre', models.CharField(max_length=100)),
                ('apellido', models.CharField(max_length=100)),
                ('telefono', models.IntegerField(blank=True, null=True)),
                ('dni', models.IntegerField(blank=True, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('pago_al_dia', models.BooleanField(default=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('materias', models.ManyToManyField(related_name='alumnos', to='estudiantes.materia')),
            ],
        ),
        migrations.CreateModel(
            name='Cuota',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nroCuota', models.IntegerField()),
                ('año', models.IntegerField()),
                ('importe', models.DecimalField(decimal_places=2, max_digits=10)),
                ('moraPrimerVencimiento', models.DecimalField(decimal_places=2, max_digits=10)),
                ('fechaPrimerVencimiento', models.DateField()),
                ('moraSegundoVencimiento', models.DecimalField(decimal_places=2, max_digits=10)),
                ('fechaSegundoVencimiento', models.DateField()),
                ('total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('importePagado', models.DecimalField(decimal_places=2, max_digits=10)),
                ('importeInformado', models.DecimalField(decimal_places=2, max_digits=10)),
                ('fechaImporteInformado', models.DateField()),
                ('estado', models.CharField(choices=[('pendiente', 'Pendiente'), ('pagado', 'Pagado'), ('informado', 'Informado')], default='pendiente', max_length=10)),
                ('alumno', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='estudiantes.alumno')),
            ],
        ),
        migrations.CreateModel(
            name='DetallePago',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monto_cuota', models.DecimalField(decimal_places=2, max_digits=10)),
                ('cuota', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='estudiantes.cuota')),
            ],
        ),
        migrations.CreateModel(
            name='FirmaCompromiso',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fechaFirma', models.DateField(auto_now_add=True)),
                ('alumno', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='estudiantes.alumno')),
            ],
        ),
        migrations.CreateModel(
            name='Inhabilitation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fechaInicio', models.DateField()),
                ('fechaFin', models.DateField()),
                ('motivo', models.CharField(max_length=255)),
                ('tipo', models.CharField(max_length=255)),
                ('alumno', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='estudiantes.alumno')),
            ],
        ),
        migrations.CreateModel(
            name='Cursado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('año', models.IntegerField()),
                ('cuatrimestre', models.IntegerField()),
                ('alumno', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='estudiantes.alumno')),
                ('materia', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='estudiantes.materia')),
            ],
        ),
        migrations.CreateModel(
            name='Mensajes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('periodo', models.CharField(max_length=255)),
                ('fechaFirma', models.DateField()),
                ('alumno', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='estudiantes.alumno')),
            ],
        ),
        migrations.CreateModel(
            name='Notificacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mensaje', models.TextField()),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('alumno', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notificaciones', to='estudiantes.alumno')),
            ],
        ),
        migrations.CreateModel(
            name='Pago',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_recibo', models.IntegerField()),
                ('monto_confirmado', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('fecha_pago_confirmado', models.DateField(blank=True, null=True)),
                ('comprobante_de_pago', models.FileField(blank=True, null=True, upload_to='comprobantes/')),
                ('forma_pago', models.CharField(choices=[('Transferencia', 'Transferencia'), ('Efectivo', 'Efectivo')], default='Transferencia', max_length=20)),
                ('alumno', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pagos', to='estudiantes.alumno')),
                ('cuotas', models.ManyToManyField(through='estudiantes.DetallePago', to='estudiantes.cuota')),
            ],
        ),
        migrations.AddField(
            model_name='detallepago',
            name='pago',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='estudiantes.pago'),
        ),
        migrations.AddField(
            model_name='cuota',
            name='pagos',
            field=models.ManyToManyField(through='estudiantes.DetallePago', to='estudiantes.pago'),
        ),
        migrations.AddConstraint(
            model_name='parametroscompromiso',
            constraint=models.UniqueConstraint(fields=('año', 'cuatrimestre'), name='unique_año_cuatrimestre'),
        ),
        migrations.AddField(
            model_name='firmacompromiso',
            name='parametros_compromiso',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='estudiantes.parametroscompromiso'),
        ),
        migrations.AlterUniqueTogether(
            name='detallepago',
            unique_together={('pago', 'cuota')},
        ),
        migrations.AlterUniqueTogether(
            name='firmacompromiso',
            unique_together={('alumno', 'parametros_compromiso')},
        ),
    ]
