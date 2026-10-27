from django.contrib import admin
from .models import EventsRegistration, EventsTeammember

# Register your models here.
# Assuming existing models might be here, I'll allow Overwrite since previous file was empty
# Wait, dashboard/admin.py was existing. I should check if I am overwriting anything important.
# Step 45 showed only "Register your models here.". So it is safe to overwrite.

class EventsTeammemberInline(admin.TabularInline):
    model = EventsTeammember
    extra = 0

@admin.register(EventsRegistration)
class EventsRegistrationAdmin(admin.ModelAdmin):
    list_display = ('project_title', 'team_leader_name', 'created_at')
    inlines = [EventsTeammemberInline]
