# Generated by Django 5.0.3 on 2024-04-18 09:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tfgWeb', '0005_alter_pathway_graphinfo'),
    ]

    operations = [
        migrations.CreateModel(
            name='Compound',
            fields=[
                ('identifier', models.CharField(max_length=6, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
            ],
        ),
    ]