from django.contrib import admin
from .models import Registration, GalleryImage

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('project_title', 'team_leader_name', 'college_selection', 'created_at')
    search_fields = ('project_title', 'team_leader_name', 'transaction_id')
    list_filter = ('college_selection', 'created_at')

@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('alt_text', 'created_at')
