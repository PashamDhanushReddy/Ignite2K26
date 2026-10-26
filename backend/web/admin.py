from django.contrib import admin
from .models import Registration, GalleryImage

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('project_title', 'team_leader_name', 'college_selection', 'project_category', 'selection_status', 'created_at')
    search_fields = ('project_title', 'team_leader_name', 'transaction_id', 'project_category')
    list_filter = ('selection_status', 'college_selection', 'project_category', 'created_at')
    list_editable = ('selection_status',)

@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('alt_text', 'created_at')
