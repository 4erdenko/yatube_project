# Generated by Django 2.2.19 on 2023-01-02 15:12

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('posts', '0005_auto_20230102_1807'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, upload_to='posts/',
                                    verbose_name='Картинка'),
        ),
    ]
