from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0002_doctorschedule'),
    ]

    operations = [
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('description', models.TextField(blank=True)),
                ('icon', models.CharField(blank=True, help_text='Font Awesome icon class, e.g. fa-tooth', max_length=120)),
                ('order', models.IntegerField(default=0, help_text='Lower numbers appear first')),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['order', 'name'],
            },
        ),
    ]
