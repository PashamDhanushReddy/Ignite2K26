from django.db import models

class WebRegistration(models.Model):
    id = models.BigAutoField(primary_key=True)
    project_title = models.CharField(max_length=255)
    team_leader_name = models.CharField(max_length=255)
    team_leader_email = models.CharField(max_length=255)
    team_leader_mobile = models.CharField(max_length=255)
    team_size = models.IntegerField()
    college_selection = models.CharField(max_length=255)
    college_name_other = models.CharField(max_length=255, blank=True, null=True)
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    payment_screenshot = models.CharField(max_length=255, blank=True, null=True)
    project_document = models.CharField(max_length=255)
    created_at = models.DateTimeField()
    selection_status = models.CharField(max_length=50, default='pending')
    idea_theme = models.CharField(max_length=255, blank=True, null=True)
    project_category = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'web_registration'
        verbose_name = 'Web Registration'
        verbose_name_plural = 'Web Registrations'

class WebTeammember(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    roll_no = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    registration = models.ForeignKey(WebRegistration, on_delete=models.DO_NOTHING)
    food_preference = models.CharField(max_length=255)
    tshirt_size = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    mobile = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'web_teammember'
