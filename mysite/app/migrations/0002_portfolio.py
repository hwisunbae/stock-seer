# Generated by Django 3.2.9 on 2021-11-29 04:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Portfolio',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('ML_method', models.CharField(choices=[('RF', 'RandomForest'), ('XG', 'XGBoost')], default='RF', max_length=2)),
                ('date', models.DateTimeField()),
                ('decision', models.CharField(max_length=5)),
                ('price', models.DecimalField(decimal_places=3, max_digits=20)),
                ('profit', models.DecimalField(decimal_places=3, max_digits=20)),
            ],
        ),
    ]