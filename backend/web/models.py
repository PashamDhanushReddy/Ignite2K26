from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from cloudinary.models import CloudinaryField

class Registration(models.Model):
    COLLEGE_CHOICES = [
        ('NRCM', 'Narsimha Reddy Engineering College'),
        ('OTHER', 'Other'),
    ]

    project_title = models.CharField(max_length=255, unique=True)
    team_leader_name = models.CharField(max_length=255)
    team_leader_email = models.EmailField()
    team_leader_mobile = models.CharField(
        max_length=10,
        validators=[RegexValidator(regex=r'^[6-9]\d{9}$', message="Mobile number must be 10 digits starting with 6-9")]
    )
    team_size = models.IntegerField(
        choices=[(i, str(i)) for i in range(2, 7)],
        validators=[MinValueValidator(2), MaxValueValidator(6)]
    )
    
    college_selection = models.CharField(max_length=10, choices=COLLEGE_CHOICES, default='NRCM')
    college_name_other = models.CharField(max_length=255, blank=True, null=True, help_text="Specify if college is not NRCM")
    
    transaction_id = models.CharField(max_length=100, unique=True, blank=True, null=True, help_text="UTR ID")
    payment_screenshot = CloudinaryField('image', blank=True, null=True)
    project_document = CloudinaryField('raw', resource_type='raw')
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.project_title

class TeamMember(models.Model):
    TSHIRT_CHOICES = [
        ('S', 'Small (S)'),
        ('M', 'Medium (M)'),
        ('L', 'Large (L)'),
        ('XL', 'Extra Large (XL)'),
        ('XXL', 'XXL'),
        ('XXXL', 'XXXL'),
    ]
    FOOD_CHOICES = [
        ('VEG', 'Vegetarian'),
        ('NON-VEG', 'Non-Vegetarian'),
    ]
    DEPT_CHOICES = [
        ('CSE', 'CSE'),
        ('AIML', 'AIML'),
        ('CSE-CS', 'CSE-CS'),
        ('CSE-DS', 'CSE-DS'),
        ('IT', 'IT'),
        ('ECE', 'ECE'),
        ('EEE', 'EEE'),
        ('MECH', 'MECH'),
        ('CIVIL', 'CIVIL'),
    ]

    registration = models.ForeignKey(Registration, related_name='team_members', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.EmailField(default='example@example.com')
    mobile = models.CharField(
        max_length=10,
        validators=[RegexValidator(regex=r'^[6-9]\d{9}$', message="Mobile number must be 10 digits starting with 6-9")],
        default='9999999999'
    )
    roll_no = models.CharField(max_length=50)
    department = models.CharField(max_length=20, choices=DEPT_CHOICES)
    tshirt_size = models.CharField(max_length=5, choices=TSHIRT_CHOICES, default='M')
    food_preference = models.CharField(max_length=10, choices=FOOD_CHOICES, default='VEG')

    def __str__(self):
        return f"{self.name} ({self.roll_no})"

class GalleryImage(models.Model):
    image = CloudinaryField('image')
    alt_text = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.alt_text or f"Image {self.id}"
