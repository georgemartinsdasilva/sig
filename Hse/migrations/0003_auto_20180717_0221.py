# Generated by Django 2.0.5 on 2018-07-17 05:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Hse', '0002_chamado_hse_resp_terc'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chamado_hse',
            name='resp_terc',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cadastro.cad_resp'),
        ),
    ]
