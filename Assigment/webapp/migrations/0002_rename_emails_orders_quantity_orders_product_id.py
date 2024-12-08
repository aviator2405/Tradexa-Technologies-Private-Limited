# Generated by Django 5.0.6 on 2024-12-07 11:12

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='orders',
            old_name='emails',
            new_name='quantity',
        ),
        migrations.AddField(
            model_name='orders',
            name='product_id',
            field=models.ForeignKey(default=django.utils.timezone.now, on_delete=django.db.models.deletion.CASCADE, to='webapp.products'),
            preserve_default=False,
        ),
    ]