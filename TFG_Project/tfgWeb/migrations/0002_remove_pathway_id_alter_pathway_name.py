# Generated by Django 5.0.3 on 2024-04-04 07:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tfgWeb', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pathway',
            name='id',
        ),
        migrations.AlterField(
            model_name='pathway',
            name='name',
            field=models.CharField(max_length=255, primary_key=True, serialize=False),
        ),
    ]
