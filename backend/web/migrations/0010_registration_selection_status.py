from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0009_registration_project_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='registration',
            name='selection_status',
            field=models.CharField(
                choices=[('PENDING', 'Pending'), ('selected', 'Selected'), ('rejected', 'Rejected')],
                default='PENDING',
                max_length=50
            ),
        ),
    ]
