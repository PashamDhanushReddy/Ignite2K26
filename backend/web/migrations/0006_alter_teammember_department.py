
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0005_alter_teammember_food_preference_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teammember',
            name='department',
            field=models.CharField(choices=[('CSE', 'CSE'), ('AIML', 'AIML'), ('CSE-CS', 'CSE-CS'), ('CSE-DS', 'CSE-DS'), ('IT', 'IT'), ('ECE', 'ECE'), ('EEE', 'EEE'), ('MECH', 'MECH'), ('CIVIL', 'CIVIL')], max_length=20),
        ),
    ]
