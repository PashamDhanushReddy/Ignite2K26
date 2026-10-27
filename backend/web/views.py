from django.shortcuts import render, redirect
from .models import Registration, TeamMember
from django.contrib import messages
from django.db import transaction, IntegrityError

def index(request):
    domains = [
        "Civil Engineering", "Computer Science", "Electronics & Comm.",
        "Information Tech", "Electrical & Electronics", "Mechanical Engg",
        "MBA", "MCA", "Science & Humanities"
    ]
    return render(request, 'web/index.html', {'domains': domains})

def register(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Extract basic info
                project_title = request.POST.get('project_title')
                
                # Team Size from hidden input or calculate (let's use hidden input which is consistent with UI)
                try:
                    team_size = int(request.POST.get('team_size', 2))
                except ValueError:
                    team_size = 2
                
                # Leader Details from Member 1
                leader_name = request.POST.get('member_name_1')
                leader_email = request.POST.get('member_email_1')
                leader_mobile = request.POST.get('member_mobile_1')
                
                # Validation (Min 2, Max 6) is handled nicely by UI, but good to be safe if manual post
                if team_size < 2: team_size = 2
                if team_size > 6: team_size = 6

                college_sel = request.POST.get('college_selection')
                college_other = request.POST.get('college_name_other') if college_sel == 'OTHER' else None
                
                trans_id = request.POST.get('transaction_id')
                
                # Check uniqueness manually
                if Registration.objects.filter(project_title=project_title).exists():
                    messages.error(request, "Project Title already exists.")
                    return render(request, 'web/register.html')
                
                # Payment validation only for Non-NRCM
                if college_sel == 'OTHER':
                    if not trans_id or not request.FILES.get('payment_screenshot'):
                        messages.error(request, "Payment details are required for non-NRCM students.")
                        return render(request, 'web/register.html')

                    if Registration.objects.filter(transaction_id=trans_id).exists():
                        messages.error(request, "Transaction ID already used.")
                        return render(request, 'web/register.html')
                else:
                    if not trans_id:
                        trans_id = None 

                # Create Registration
                reg = Registration.objects.create(
                    project_title=project_title,
                    team_leader_name=leader_name,
                    team_leader_email=leader_email,
                    team_leader_mobile=leader_mobile,
                    team_size=team_size,
                    college_selection=college_sel,
                    college_name_other=college_other,
                    transaction_id=trans_id,
                    payment_screenshot=request.FILES.get('payment_screenshot') if college_sel == 'OTHER' else None,
                    project_document=request.FILES.get('project_document')
                )

                # Create Team Members
                for i in range(1, team_size + 1):
                    name = request.POST.get(f'member_name_{i}')
                    email = request.POST.get(f'member_email_{i}')
                    mobile = request.POST.get(f'member_mobile_{i}')
                    roll = request.POST.get(f'member_roll_{i}')
                    dept = request.POST.get(f'member_dept_{i}')
                    tshirt = request.POST.get(f'member_tshirt_{i}')
                    food = request.POST.get(f'member_food_{i}')
                    
                    TeamMember.objects.create(
                        registration=reg,
                        name=name,
                        email=email,
                        mobile=mobile,
                        roll_no=roll,
                        department=dept,
                        tshirt_size=tshirt,
                        food_preference=food
                    )
                
                messages.success(request, "Registration successful! Good luck for Ignite 2K27.")
                return redirect('success')

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return render(request, 'web/register.html')

    return render(request, 'web/register.html')


def success(request):
    return render(request, 'web/success.html')

from django.http import JsonResponse
from django.templatetags.static import static
from .models import GalleryImage

def gallery_api(request):
    # Curated official Ignite 2K26/2K27 Expo photos
    expo_photos = [
        'SSV07033', 'SSV07054', 'SSV07027', 'SSV07026', 'SSV06674',
        'SSV06660', 'SSV06609', 'SSV06598', 'SSV06287', 'SSV06259',
        'SSV06254', 'SSV06243', 'SSV06239', 'SSV06207'
    ]
    data = [
        {
            'url': static(f'web/images/gallery/{name}.webp'),
            'fallback_url': static(f'web/images/gallery/{name}.jpg'),
            'original_url': static(f'web/images/{name}.JPG'),
            'alt': f'Ignite Expo Photo {name}'
        }
        for name in expo_photos
    ]
    return JsonResponse({'images': data})
