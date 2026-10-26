from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0008_teammember_email_teammember_mobile'),
    ]

    operations = [
        migrations.AddField(
            model_name='registration',
            name='project_category',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
    ]
