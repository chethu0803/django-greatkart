# Generated by Django 5.1.1 on 2024-10-26 07:28

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0008_alter_product_images'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productgallery',
            name='image',
            field=cloudinary.models.CloudinaryField(max_length=255, verbose_name='image'),
        ),
    ]
