from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.conf import settings
import base64
import urllib.parse
import csv
import json
from datetime import datetime
import pandas as pd
from io import BytesIO
from django.utils.dateparse import parse_datetime
from django.db.models import Q

# Import models
from website_fixed.models import WebRegistration, WebTeammember

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'dashboard/login.html')

@login_required(login_url='login')
def update_selection_status_view(request):
    """
    API endpoint to update the selection status of a registration.
    Expects POST request with registration_id and selection_status.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        registration_id = data.get('registration_id')
        selection_status = data.get('selection_status')
        
        if not registration_id or not selection_status:
            return JsonResponse({'error': 'registration_id and selection_status are required'}, status=400)
        
        valid_statuses = ['pending', 'selected', 'rejected', 'waitlisted']
        if selection_status not in valid_statuses:
            return JsonResponse({'error': f'Invalid selection_status. Must be one of: {", ".join(valid_statuses)}'}, status=400)
        
        # Update the status in the actual database
        try:
            WebRegistration.objects.filter(id=registration_id).update(selection_status=selection_status)
            
            return JsonResponse({
                'success': True, 
                'message': 'Status updated successfully',
                'registration_id': registration_id,
                'new_status': selection_status
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def debug_storage_view(request):
    # Stubbed out as Supabase client is removed
    return render(request, 'dashboard/debug_storage.html', {'error': 'Supabase direct access disabled'})

@login_required(login_url='login')
def debug_fields_view(request):
    # Use ORM to inspect first object
    first_reg = WebRegistration.objects.first()
    context = {
        'registration': first_reg,
        'fields': [f.name for f in WebRegistration._meta.get_fields()],
        'sample_data': first_reg.__dict__ if first_reg else {}
    }
    return render(request, 'dashboard/debug_fields.html', context)

@login_required(login_url='login')
def dashboard_view(request):
    # Get filter parameters
    # college_code_filter removed
    team_size_filter = request.GET.get('team_size', '')
    has_ppt_filter = request.GET.get('has_ppt', '')
    date_filter = request.GET.get('date', '')
    idea_theme_filter = request.GET.get('idea_theme', '')
    project_category_filter = request.GET.get('project_category', '')
    selection_status_filter = request.GET.get('selection_status', '')
    
    # Base Query
    registrations_qs = WebRegistration.objects.all().prefetch_related('webteammember_set').order_by('-created_at')

    # Apply Filters
    if team_size_filter:
        registrations_qs = registrations_qs.filter(team_size=team_size_filter)
    
    if has_ppt_filter == 'yes':
        registrations_qs = registrations_qs.exclude(project_document='')
    elif has_ppt_filter == 'no':
        registrations_qs = registrations_qs.filter(project_document='')
        
    if date_filter:
        # Assuming date_filter is YYYY-MM-DD
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            registrations_qs = registrations_qs.filter(created_at__date=filter_date)
        except ValueError:
            pass
            
    # college_code_filter logic removed

    if idea_theme_filter:
        registrations_qs = registrations_qs.filter(idea_theme=idea_theme_filter)

    if project_category_filter:
        registrations_qs = registrations_qs.filter(project_category=project_category_filter)

    if selection_status_filter:
        registrations_qs = registrations_qs.filter(selection_status=selection_status_filter)

    # Process Data
    processed_registrations = []
    
    # Dropdown collections
    # all_college_codes removed
    tshirt_counts = {'S': 0, 'M': 0, 'L': 0, 'XL': 0, 'XXL': 0, 'XXXL': 0}
    food_counts = {'veg': 0, 'nonveg': 0}
    
    # We need a separate pass for aggregates if we filter the main list? 
    # The original code aggregated on UNFILTERED list.
    all_regs_for_stats = WebRegistration.objects.all().prefetch_related('webteammember_set')
    
    for reg in all_regs_for_stats:
        # college_code aggregation removed
        
        members = reg.webteammember_set.all()
        for m in members:
            ts = (m.tshirt_size or '').upper()
            if ts in tshirt_counts:
                tshirt_counts[ts] += 1
            
            fp = (m.food_preference or '').lower()
            if 'veg' in fp and 'non' not in fp:
                food_counts['veg'] += 1
            elif 'non' in fp:
                food_counts['nonveg'] += 1

    # Main Loop for Display
    for reg in registrations_qs:
        
        ppt_path = reg.project_document or ''
        has_ppt = bool(ppt_path)
        
        # Build Team Members List
        members = reg.webteammember_set.all()
        team_members_list = []
        detailed_members = []
        
        for i, m in enumerate(members, 1):
            is_leader = (m.name == reg.team_leader_name)
            
            member_dict = {
                'name': m.name,
                'email': m.email,
                'phone': m.mobile,
                'roll': m.roll_no,
                'gender': 'N/A', # Missing
                'year': 'N/A', # Missing
                'college': reg.college_selection,
                'college_code': 'N/A',
                'course': m.department, # Mapping department -> course
                'tshirt_size': m.tshirt_size,
                'food_preference': m.food_preference,
                'is_leader': is_leader
            }
            team_members_list.append(member_dict)
            
            detailed_info = member_dict.copy()
            detailed_members.append(detailed_info)
        
        # Handle "Other" college selection
        college_display = reg.college_selection
        if (str(college_display).lower() == 'other') and reg.college_name_other:
            college_display = reg.college_name_other

        essential_data = {
            'id': reg.id,
            'team_name': reg.project_title, # Fallback
            'team_leader_name': reg.team_leader_name,
            'team_leader_email': reg.team_leader_email,
            'team_leader_phone': reg.team_leader_mobile,
            'college_name': college_display,
            # 'college_code': 'N/A', # Removed
            'team_size': reg.team_size,
            'registration_date': reg.created_at,
            'has_ppt': has_ppt,
            'idea_title': reg.project_title,
            'idea_theme': reg.idea_theme,
            'project_category': reg.project_category,
            'youtube_link': 'N/A', # Missing
            'ppt_file_path': ppt_path,
            'selection_status': reg.selection_status,
            'transaction_id': reg.transaction_id,
        }
        
        essential_data['team_members'] = team_members_list
        essential_data['team_members_json'] = json.dumps(team_members_list)
        essential_data['Detailed Members'] = detailed_members # For export view
        
        # Document URLs
        
        # 1. Abstract / Project Document
        if ppt_path:
             if ppt_path.startswith('http'):
                 essential_data['abstract_url'] = ppt_path
             else:
                 cloud_name = settings.CLOUDINARY_STORAGE.get('CLOUD_NAME')
                 if cloud_name:
                     essential_data['abstract_url'] = f"https://res.cloudinary.com/{cloud_name}/{ppt_path}"
                 else:
                     essential_data['abstract_url'] = '#'
        
        # 2. Payment Proof
        payment_proof_path = reg.payment_screenshot or ''
        if payment_proof_path:
             if payment_proof_path.startswith('http'):
                 essential_data['payment_proof_url'] = payment_proof_path
             else:
                 cloud_name = settings.CLOUDINARY_STORAGE.get('CLOUD_NAME')
                 if cloud_name:
                     essential_data['payment_proof_url'] = f"https://res.cloudinary.com/{cloud_name}/{payment_proof_path}"
                 else:
                     essential_data['payment_proof_url'] = '#'
                     
        processed_registrations.append(essential_data)

    total_registrations = WebRegistration.objects.count()
    
    context = {
        'registrations': processed_registrations,
        'filters': {
            # 'college_code': college_code_filter,
            'team_size': team_size_filter,
            'has_ppt': has_ppt_filter,
            'date': date_filter,
            'idea_theme': idea_theme_filter,
            'project_category': project_category_filter,
            'selection_status': selection_status_filter,
        },
        'college_codes': [], # Empty list instead of removed var
        'team_sizes': ['2', '3', '4', '5', '6'],
        'idea_themes': list(WebRegistration.objects.values_list('idea_theme', flat=True).distinct()),
        'project_categories': list(WebRegistration.objects.values_list('project_category', flat=True).distinct().exclude(project_category__isnull=True).exclude(project_category='')),
        'total_registrations': total_registrations,
        'tshirt_counts': tshirt_counts,
        'food_counts': food_counts,
    }
    
    return render(request, 'dashboard/dashboard.html', context)

@login_required(login_url='login')
def download_ppt_view(request, ppt_path):
    return HttpResponse("Download unavailable - Storage credentials not configured.", status=503)

@login_required(login_url='login')
def export_registrations_view(request):
    # Use dashboard_view logic to get processed data
    # Hack: call dashboard_view internal logic or copy-paste. 
    # For simplicitly, let's copy the query logic since we want to return CSV
    
    # ... (Reusing query logic from dashboard_view) ...
    # Base Query
    registrations_qs = WebRegistration.objects.all().prefetch_related('webteammember_set').order_by('-created_at')
    
    # Process Filter Params (Duplicated from dashboard_view)
    college_code_filter = request.GET.get('college_code', '')
    team_size_filter = request.GET.get('team_size', '')
    has_ppt_filter = request.GET.get('has_ppt', '')

    date_filter = request.GET.get('date', '')
    idea_theme_filter = request.GET.get('idea_theme', '')
    selection_status_filter = request.GET.get('selection_status', '')

    if team_size_filter:
        registrations_qs = registrations_qs.filter(team_size=team_size_filter)
    if has_ppt_filter == 'yes':
        registrations_qs = registrations_qs.exclude(project_document='')
    elif has_ppt_filter == 'no':
        registrations_qs = registrations_qs.filter(project_document='')
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            registrations_qs = registrations_qs.filter(created_at__date=filter_date)
        except ValueError:
            pass
            
    if idea_theme_filter:
         registrations_qs = registrations_qs.filter(idea_theme=idea_theme_filter)

    if selection_status_filter:
         registrations_qs = registrations_qs.filter(selection_status=selection_status_filter)
    if college_code_filter:
        registrations_qs = registrations_qs.filter(Q(college_selection__icontains=college_code_filter) | Q(college_name_other__icontains=college_code_filter))


    # Map to export format
    processed_data = []
    for reg in registrations_qs:
        ppt_path = reg.project_document or ''
        
        # Members string
        members = reg.webteammember_set.all()
        members_list_str = []
        detailed_members = []
        
        for m in members:
            member_str = f"{m.name} ({m.roll_no})"
            if m.name == reg.team_leader_name:
                member_str += " [LEADER]"
            members_list_str.append(member_str)
            
            detailed_members.append({
                'name': m.name,
                'email': m.email,
                'phone': m.mobile,
                'roll': m.roll_no,
                'food_preference': m.food_preference,
                'is_leader': (m.name == reg.team_leader_name)
            })

        # Handle "Other" college selection for export
        college_display = reg.college_selection
        if (str(college_display).lower() == 'other') and reg.college_name_other:
            college_display = reg.college_name_other

        processed_data.append({
            'Team Name': reg.project_title,
            'Team Leader': reg.team_leader_name,
            'Leader Email': reg.team_leader_email,
            'Leader Phone': reg.team_leader_mobile,
            'College': college_display,
            'College Code': 'N/A',
            'Team Size': reg.team_size,
            'Payment Status': 'pending', 
            'Team Members': "; ".join(members_list_str),
            'Registration Date': reg.created_at,
            'Idea Title': reg.project_title,
            'Payment Proof': ppt_path,
            'Detailed Members': detailed_members,
        })
        
    # Check export format
    export_format = request.GET.get('format', 'csv')
    
    if export_format == 'excel':
        # Create detailed DataFrame
        detailed_rows = []
        for reg in processed_data:
            base_row = {k: v for k, v in reg.items() if k != 'Detailed Members'}
            
            if reg.get('Detailed Members'):
                for i, member in enumerate(reg['Detailed Members'], 1):
                    base_row[f'Member {i} Name'] = member['name']
                    base_row[f'Member {i} Roll No'] = member['roll']
                    base_row[f'Member {i} Email'] = member['email']
                    base_row[f'Member {i} Phone'] = member['phone']
                    base_row[f'Member {i} Food Preference'] = member['food_preference']
                    base_row[f'Member {i} Role'] = 'Team Leader' if member['is_leader'] else 'Member'
            detailed_rows.append(base_row)
            
        df = pd.DataFrame(detailed_rows)
        
        # Remove timezone from datetimes
        if 'Registration Date' in df.columns:
            df['Registration Date'] = df['Registration Date'].apply(lambda x: x.replace(tzinfo=None) if x else x)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Registrations')
        output.seek(0)
        
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="registrations.xlsx"'
        return response

    # CSV Default
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="registrations.csv"'
    
    # Flatten for CSV (simplified vs previous complex logic)
    detailed_rows = []
    for reg in processed_data:
        base_row = {k: v for k, v in reg.items() if k != 'Detailed Members'}
        detailed_rows.append(base_row)
        
    if detailed_rows:
        writer = csv.DictWriter(response, fieldnames=detailed_rows[0].keys())
        writer.writeheader()
        writer.writerows(detailed_rows)
        
    return response
