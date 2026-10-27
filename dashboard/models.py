from django.db import models

class EventsRegistration(models.Model):
    id = models.BigAutoField(primary_key=True)
    project_title = models.CharField(max_length=255)
    team_leader_name = models.CharField(max_length=255)
    team_leader_email = models.CharField(max_length=255)
    team_leader_mobile = models.CharField(max_length=255)
    team_size = models.IntegerField()
    college_name = models.CharField(max_length=255)
    other_college_name = models.CharField(max_length=255, blank=True, null=True)
    utr_id = models.CharField(max_length=255)
    payment_screenshot = models.CharField(max_length=255)
    project_document = models.CharField(max_length=255)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'events_registration'
        verbose_name = 'Event Registration'
        verbose_name_plural = 'Event Registrations'

class EventsTeammember(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    roll_no = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    registration = models.ForeignKey(EventsRegistration, on_delete=models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'events_teammember'
