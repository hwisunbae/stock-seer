# Generated by Django 3.2.9 on 2021-11-22 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Stock',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateField()),
                ('adj_close', models.DecimalField(decimal_places=17, max_digits=20)),
                ('close', models.DecimalField(decimal_places=17, max_digits=20)),
                ('volume', models.DecimalField(decimal_places=0, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='Tweets',
            fields=[
                ('id', models.DecimalField(decimal_places=0, max_digits=19)),
                ('created_at', models.DateTimeField()),
                ('user_name', models.CharField(max_length=300)),
                ('text', models.CharField(max_length=400)),
                ('lang', models.CharField(max_length=5)),
                ('tokens', models.CharField(max_length=300)),
                ('subjectivity', models.DecimalField(decimal_places=3, max_digits=3)),
                ('polarity', models.DecimalField(decimal_places=3, max_digits=3)),
                ('analysis', models.DecimalField(decimal_places=0, max_digits=2)),
                ('_id', models.AutoField(primary_key=True, serialize=False)),
            ],
        ),
    ]
