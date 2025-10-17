from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe_name', models.CharField(max_length=255)),
                ('cook_time', models.DurationField(blank=True, null=True)),
                ('prep_time', models.DurationField(blank=True, null=True)),
                ('total_time', models.DurationField(blank=True, null=True)),
                ('ingredients', models.TextField(blank=True, null=True)),
                ('calories', models.FloatField(blank=True, null=True)),
                ('fat', models.FloatField(blank=True, null=True)),
                ('saturated_fat', models.FloatField(blank=True, null=True)),
                ('cholesterol', models.FloatField(blank=True, null=True)),
                ('sodium', models.FloatField(blank=True, null=True)),
                ('carbohydrate', models.FloatField(blank=True, null=True)),
                ('fiber', models.FloatField(blank=True, null=True)),
                ('sugar', models.FloatField(blank=True, null=True)),
                ('protein', models.FloatField(blank=True, null=True)),
                ('instructions', models.TextField(blank=True, null=True)),
                ('type', models.CharField(blank=True, max_length=50, null=True)),
                ('cuisine', models.CharField(blank=True, max_length=100, null=True)),
                ('image', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
    ]
