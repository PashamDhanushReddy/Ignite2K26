from django.contrib import admin
from .models import WebRegistration, WebTeammember

class WebTeammemberInline(admin.TabularInline):
    model = WebTeammember
    extra = 0

@admin.register(WebRegistration)
class WebRegistrationAdmin(admin.ModelAdmin):
    list_display = ('project_title', 'team_leader_name', 'created_at')
    inlines = [WebTeammemberInline]
    actions = ['export_to_excel']

    def export_to_excel(self, request, queryset):
        import openpyxl
        from django.http import HttpResponse

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = 'attachment; filename={date}-registrations.xlsx'.format(
            date=queryset.first().created_at.strftime('%Y-%m-%d') if queryset.exists() else 'export',
        )
        
        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        worksheet.title = 'Registrations'

        # Define columns
        columns = [
            'Registration ID', 'Project Title', 'Team Leader Name', 'Team Leader Email', 'Team Leader Mobile',
            'Team Size', 'College Selection', 'College Name Other', 'Transaction ID', 'Using Alternate UPI',
            'Project Document', 'Created At', 'Selection Status', 'Project Category',
            'Member Name', 'Member Roll No', 'Member Department', 'Member Food Preference',
            'Member T-Shirt Size', 'Member Email', 'Member Mobile'
        ]

        # Write header row
        for col_num, column_title in enumerate(columns, 1):
            cell = worksheet.cell(row=1, column=col_num)
            cell.value = column_title

        # Write data rows
        row_num = 2
        for registration in queryset:
            members = registration.webteammember_set.all()
            
            # If no members, still print the registration details
            if not members.exists():
                row = [
                    registration.id, registration.project_title, registration.team_leader_name,
                    registration.team_leader_email, registration.team_leader_mobile, registration.team_size,
                    registration.college_selection, registration.college_name_other, registration.transaction_id,
                    registration.payment_screenshot, # Using payment_screenshot field for now as per model, might verify purpose
                    registration.project_document, registration.created_at.replace(tzinfo=None) if registration.created_at else '',
                    registration.selection_status, registration.project_category,
                    '', '', '', '', '', '', '' # Empty member fields
                ]
                for col_num, cell_value in enumerate(row, 1):
                    cell = worksheet.cell(row=row_num, column=col_num)
                    cell.value = cell_value
                row_num += 1
            else:
                for member in members:
                    row = [
                        registration.id, registration.project_title, registration.team_leader_name,
                        registration.team_leader_email, registration.team_leader_mobile, registration.team_size,
                        registration.college_selection, registration.college_name_other, registration.transaction_id,
                        registration.payment_screenshot,
                        registration.project_document, registration.created_at.replace(tzinfo=None) if registration.created_at else '',
                        registration.selection_status, registration.project_category,
                        member.name, member.roll_no, member.department, member.food_preference,
                        member.tshirt_size, member.email, member.mobile
                    ]
                    for col_num, cell_value in enumerate(row, 1):
                        cell = worksheet.cell(row=row_num, column=col_num)
                        cell.value = cell_value
                    row_num += 1

        workbook.save(response)
        return response

    export_to_excel.short_description = 'Export to Excel'
