# Generated by Django 4.0 on 2022-01-04 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_alter_filesmodel_file_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='filesmodel',
            name='file_type',
            field=models.CharField(choices=[('text', 'text'), ('video', 'video'), ('sound', 'sound'), ('image', 'image')], default=('text', 'text'), max_length=50),
        ),
    ]
