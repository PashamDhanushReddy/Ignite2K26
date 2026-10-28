import os
import threading
import urllib.request
import urllib.error
import json
from email.utils import parseaddr
from django.shortcuts import render, redirect
from .models import Registration, TeamMember
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings

def index(request):
    domains = [
        "Civil Engineering", "Computer Science", "Electronics & Comm.",
        "Information Tech", "Electrical & Electronics", "Mechanical Engg",
        "MBA", "MCA", "Science & Humanities"
    ]
    return render(request, 'web/index.html', {'domains': domains})

import re
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

ALLOWED_DOC_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx'}
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
MAX_DOC_SIZE = 10 * 1024 * 1024   # 10 MB
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB

VALID_DEPARTMENTS = {'CSE', 'AIML', 'CSE-CS', 'CSE-DS', 'IT', 'ECE', 'EEE', 'MECH', 'CIVIL'}
VALID_TSHIRTS = {'S', 'M', 'L', 'XL', 'XXL', 'XXXL'}
VALID_FOODS = {'VEG', 'NON-VEG'}

def register(request):
    if request.method == 'POST':
        try:
            # 1. Anti-spam honeypot detection
            if request.POST.get('website_hp'):
                messages.error(request, "Registration request rejected due to suspicious activity.")
                return render(request, 'web/register.html')

            # 2. Project Title validation
            project_title = (request.POST.get('project_title') or '').strip()
            if not project_title or len(project_title) < 3:
                messages.error(request, "Please enter a valid Project Title (at least 3 characters).")
                return render(request, 'web/register.html')

            if len(project_title) > 255:
                messages.error(request, "Project Title must be 255 characters or fewer.")
                return render(request, 'web/register.html')

            if Registration.objects.filter(project_title__iexact=project_title).exists():
                messages.error(request, f"A project with the title '{project_title}' has already been registered.")
                return render(request, 'web/register.html')

            # 3. Team size validation
            try:
                team_size = int(request.POST.get('team_size', 2))
                if team_size < 2 or team_size > 6:
                    messages.error(request, "Team size must be between 2 and 6 members.")
                    return render(request, 'web/register.html')
            except (ValueError, TypeError):
                messages.error(request, "Invalid team size specified.")
                return render(request, 'web/register.html')

            # 4. College Selection & Payment details validation
            college_sel = request.POST.get('college_selection', 'NRCM')
            if college_sel not in ('NRCM', 'OTHER'):
                college_sel = 'NRCM'

            college_other = None
            trans_id = (request.POST.get('transaction_id') or '').strip() or None
            payment_screenshot = request.FILES.get('payment_screenshot')

            if college_sel == 'OTHER':
                college_other = (request.POST.get('college_name_other') or '').strip()
                if not college_other or len(college_other) < 2:
                    messages.error(request, "Please specify your Institution / College name.")
                    return render(request, 'web/register.html')

                if not trans_id:
                    messages.error(request, "Transaction / UTR ID is required for non-NRCM college registrations.")
                    return render(request, 'web/register.html')

                if not payment_screenshot:
                    messages.error(request, "Payment screenshot is required for non-NRCM college registrations.")
                    return render(request, 'web/register.html')

            if trans_id:
                if Registration.objects.filter(transaction_id__iexact=trans_id).exists():
                    messages.error(request, f"The Transaction / UTR ID '{trans_id}' has already been used.")
                    return render(request, 'web/register.html')

            # 5. File upload validation (Screenshots)
            if payment_screenshot:
                if payment_screenshot.size > MAX_IMAGE_SIZE:
                    messages.error(request, "Payment screenshot file size must be under 5MB.")
                    return render(request, 'web/register.html')
                img_ext = os.path.splitext(payment_screenshot.name)[1].lower().lstrip('.')
                if img_ext not in ALLOWED_IMAGE_EXTENSIONS:
                    messages.error(request, f"Invalid payment screenshot format (.{img_ext}). Allowed formats: JPG, JPEG, PNG, WEBP.")
                    return render(request, 'web/register.html')

            # 6. File upload validation (Project Document / Abstract)
            project_doc = request.FILES.get('project_document')
            if not project_doc:
                messages.error(request, "Project abstract / presentation document is required.")
                return render(request, 'web/register.html')

            if project_doc.size > MAX_DOC_SIZE:
                messages.error(request, "Project document file size must be under 10MB.")
                return render(request, 'web/register.html')

            doc_ext = os.path.splitext(project_doc.name)[1].lower().lstrip('.')
            if doc_ext not in ALLOWED_DOC_EXTENSIONS:
                messages.error(request, f"Invalid project document format (.{doc_ext}). Allowed formats: PDF, DOC, DOCX, PPT, PPTX.")
                return render(request, 'web/register.html')

            # 7. Team Members validation
            mobile_regex = re.compile(r'^[6-9]\d{9}$')
            members_data = []
            seen_roll_numbers = set()
            seen_emails = set()
            seen_mobiles = set()

            for i in range(1, team_size + 1):
                name = (request.POST.get(f'member_name_{i}') or '').strip()
                email = (request.POST.get(f'member_email_{i}') or '').strip().lower()
                mobile = (request.POST.get(f'member_mobile_{i}') or '').strip()
                roll = (request.POST.get(f'member_roll_{i}') or '').strip().upper()
                dept = (request.POST.get(f'member_dept_{i}') or '').strip().upper()
                tshirt = (request.POST.get(f'member_tshirt_{i}') or 'M').strip().upper()
                food = (request.POST.get(f'member_food_{i}') or 'VEG').strip().upper()

                label = f"Team Leader (Member 1)" if i == 1 else f"Member {i}"

                if not name or len(name) < 2:
                    messages.error(request, f"Please enter a valid full name for {label}.")
                    return render(request, 'web/register.html')

                if not email:
                    messages.error(request, f"Email ID is required for {label}.")
                    return render(request, 'web/register.html')
                try:
                    validate_email(email)
                except ValidationError:
                    messages.error(request, f"Invalid email ID '{email}' entered for {label}.")
                    return render(request, 'web/register.html')

                if email in seen_emails:
                    messages.error(request, f"Duplicate email '{email}' found for multiple team members.")
                    return render(request, 'web/register.html')
                seen_emails.add(email)

                if not mobile or not mobile_regex.match(mobile):
                    messages.error(request, f"Invalid mobile number for {label}. Must be a 10-digit number starting with 6-9.")
                    return render(request, 'web/register.html')

                if mobile in seen_mobiles:
                    messages.error(request, f"Duplicate mobile '{mobile}' found for multiple team members.")
                    return render(request, 'web/register.html')
                seen_mobiles.add(mobile)

                if not roll:
                    messages.error(request, f"Hall ticket / Roll number is required for {label}.")
                    return render(request, 'web/register.html')

                if roll in seen_roll_numbers:
                    messages.error(request, f"Duplicate roll number '{roll}' found in team members.")
                    return render(request, 'web/register.html')
                seen_roll_numbers.add(roll)

                if dept not in VALID_DEPARTMENTS:
                    messages.error(request, f"Please select a valid department for {label}.")
                    return render(request, 'web/register.html')

                if tshirt not in VALID_TSHIRTS:
                    tshirt = 'M'
                if food not in VALID_FOODS:
                    food = 'VEG'

                members_data.append({
                    'name': name,
                    'email': email,
                    'mobile': mobile,
                    'roll_no': roll,
                    'department': dept,
                    'tshirt_size': tshirt,
                    'food_preference': food,
                })

            # 8. Create Registration and Team Members in Atomic Transaction
            with transaction.atomic():
                reg = Registration.objects.create(
                    project_title=project_title,
                    team_leader_name=members_data[0]['name'],
                    team_leader_email=members_data[0]['email'],
                    team_leader_mobile=members_data[0]['mobile'],
                    team_size=team_size,
                    college_selection=college_sel,
                    college_name_other=college_other,
                    transaction_id=trans_id,
                    payment_screenshot=payment_screenshot if college_sel == 'OTHER' else None,
                    project_document=project_doc,
                    project_category=members_data[0]['department']
                )

                created_members = []
                for m in members_data:
                    tm = TeamMember.objects.create(
                        registration=reg,
                        name=m['name'],
                        email=m['email'],
                        mobile=m['mobile'],
                        roll_no=m['roll_no'],
                        department=m['department'],
                        tshirt_size=m['tshirt_size'],
                        food_preference=m['food_preference']
                    )
                    created_members.append(tm)

                college_name = 'Narsimha Reddy Engineering College (NRCM)'
                if reg.college_selection == 'OTHER' and reg.college_name_other:
                    college_name = reg.college_name_other

                # GUARANTEE: Email is dispatched ONLY IF the database transaction successfully commits!
                transaction.on_commit(lambda: threading.Thread(
                    target=send_registration_email,
                    args=(reg, created_members, college_name),
                    daemon=False
                ).start())

            # Store successful registration ID in session
            request.session['registration_id'] = reg.id
            messages.success(request, "Registration successful! Good luck for Ignite 2K27.")
            return redirect('success')

        except IntegrityError as ie:
            request.session.pop('registration_id', None)
            messages.error(request, "A database conflict occurred (e.g. duplicate title or transaction ID). Please check your details and try again.")
            return render(request, 'web/register.html')
        except Exception as e:
            request.session.pop('registration_id', None)
            messages.error(request, f"Registration could not be completed: {str(e)}")
            return render(request, 'web/register.html')

    return render(request, 'web/register.html')



def send_registration_email(reg, members, college_name):
    member_rows = ''.join(
        f'<tr><td style="padding:6px 10px;border:1px solid #e2e8f0;">{i+1}</td>'
        f'<td style="padding:6px 10px;border:1px solid #e2e8f0;">{m.name}</td>'
        f'<td style="padding:6px 10px;border:1px solid #e2e8f0;">{m.department}</td>'
        f'<td style="padding:6px 10px;border:1px solid #e2e8f0;">{m.roll_no}</td></tr>'
        for i, m in enumerate(members)
    )

    trans_display = reg.transaction_id if reg.transaction_id else ('NRCM Student – Recorded' if reg.college_selection == 'NRCM' else 'Recorded')

    html_body = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="color-scheme" content="light">
<style>
  body {{ font-family: Arial, sans-serif; background: #f3f4f6; margin: 0; padding: 20px; color: #1e293b; color-scheme: light; }}
  .card {{ background: #fff; border-radius: 12px; max-width: 600px; margin: 0 auto; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }}
  .header {{ background: linear-gradient(135deg, #ff3b5c, #8b5cf6); padding: 32px 24px; text-align: center; color: #fff; }}
  .header h1 {{ margin: 0; font-size: 28px; font-weight: 900; letter-spacing: 2px; }}
  .header p {{ margin: 6px 0 0; font-size: 13px; opacity: 0.9; }}
  .body {{ padding: 28px 24px; }}
  .badge {{ display: inline-block; background: #dcfce7; color: #16a34a; font-size: 12px; font-weight: 700; padding: 4px 12px; border-radius: 20px; margin-bottom: 16px; }}
  .section-title {{ font-size: 11px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; color: #94a3b8; margin: 20px 0 8px; }}
  .info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 20px; }}
  .info-item {{ background: #f8fafc; border-radius: 8px; padding: 12px; }}
  .info-item .label {{ font-size: 10px; color: #94a3b8; font-weight: 600; text-transform: uppercase; }}
  .info-item .value {{ font-size: 14px; color: #1e293b; font-weight: 700; margin-top: 2px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  th {{ background: #f1f5f9; padding: 8px 10px; text-align: left; border: 1px solid #e2e8f0; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: #64748b; }}
  .alert {{ background: #eff6ff; border-left: 4px solid #3b82f6; border-radius: 6px; padding: 14px 16px; margin-top: 20px; font-size: 13px; color: #1e40af; }}
  .whatsapp {{ background: #dcfce7; border-left: 4px solid #16a34a; border-radius: 6px; padding: 14px 16px; margin-top: 12px; font-size: 13px; color: #14532d; }}
  .footer {{ background: #f8fafc; border-top: 1px solid #e2e8f0; padding: 16px 24px; text-align: center; font-size: 11px; color: #94a3b8; }}
</style>
</head>
<body>
<div class="card">
  <div class="header">
    <h1>IGNITE 2K27</h1>
    <p>National Level Project Expo · Narsimha Reddy Engineering College</p>
  </div>
  <div class="body">
    <div class="badge">✅ Registration Confirmed</div>
    <p style="font-size:15px;margin:0 0 20px;">Dear <strong>{reg.team_leader_name}</strong>, your team has been successfully registered for <strong>Ignite 2K27</strong>!</p>
    
    <div class="section-title">Registration Details</div>
    <div class="info-grid">
      <div class="info-item"><div class="label">Project Title</div><div class="value">{reg.project_title}</div></div>
      <div class="info-item"><div class="label">College</div><div class="value">{college_name}</div></div>
      <div class="info-item"><div class="label">Team Size</div><div class="value">{reg.team_size} Members</div></div>
      <div class="info-item"><div class="label">Transaction / UTR ID</div><div class="value" style="font-family:monospace;">{trans_display}</div></div>
      <div class="info-item" style="grid-column:1/-1;"><div class="label">Event Date</div><div class="value" style="color:#dc2626;">February 26, 2027</div></div>
    </div>

    <div class="section-title">Team Members</div>
    <table>
      <thead><tr><th>#</th><th>Name</th><th>Department</th><th>Roll No.</th></tr></thead>
      <tbody>{member_rows}</tbody>
    </table>

    <div class="alert">
      📋 <strong>Next Steps:</strong> Keep your project presentation and working model/prototype ready for the offline expo on <strong>February 26, 2027</strong> at NRCM Campus, Maisammaguda (V), Kompally, Hyderabad.
    </div>
    <div class="whatsapp">
      📱 <strong>Join the official WhatsApp group</strong> for updates:<br>
      <a href="https://chat.whatsapp.com/DjPvw8V5RANCUzECRVVt80" style="color:#16a34a;">https://chat.whatsapp.com/DjPvw8V5RANCUzECRVVt80</a>
    </div>
  </div>
  <div class="footer">© 2027 IGNITE · Narsimha Reddy Engineering College. All rights reserved.</div>
</div>
</body>
</html>
"""

    plain_text = (
        f"IGNITE 2K27 - Registration Confirmed\n\n"
        f"Dear {reg.team_leader_name},\n\n"
        f"Your team has been successfully registered!\n\n"
        f"Project Title: {reg.project_title}\n"
        f"College: {college_name}\n"
        f"Team Size: {reg.team_size} members\n"
        f"Transaction ID: {trans_display}\n"
        f"Event Date: February 26, 2027\n\n"
        f"WhatsApp Group: https://chat.whatsapp.com/DjPvw8V5RANCUzECRVVt80\n\n"
        f"Venue: NRCM Campus, Maisammaguda (V), Kompally, Hyderabad, Telangana.\n\n"
        f"All the best!\nIgnite 2K27 Organizing Committee"
    )

    recipient_emails = list({m.email.strip() for m in members if m.email and m.email.strip()})
    if reg.team_leader_email and reg.team_leader_email.strip() and reg.team_leader_email.strip() not in recipient_emails:
        recipient_emails.append(reg.team_leader_email.strip())
    recipient_emails = [e for e in recipient_emails if '@' in e]

    if not recipient_emails:
        print("[Ignite Email] No valid recipient emails found. Skipping email.", flush=True)
        return

    subject = '🎉 Registration Confirmed – Ignite 2K27 | NRCM'
    from_name = 'IGNITE 2K27'
    from_email = 'ignite2k27@gmail.com'
    try:
        from email.utils import parseaddr
        parsed_name, parsed_email = parseaddr(settings.DEFAULT_FROM_EMAIL)
        if parsed_email:
            from_email = parsed_email
        if parsed_name:
            from_name = parsed_name
    except Exception:
        pass

    brevo_api_key = getattr(settings, 'BREVO_API_KEY', '') or os.environ.get('BREVO_API_KEY', '')

    if brevo_api_key and brevo_api_key.strip():
        try:
            import urllib.request
            import urllib.error
            import json

            print(f"[Ignite Email] Sending via Brevo HTTPS REST API (port 443) to {recipient_emails}...", flush=True)
            url = 'https://api.brevo.com/v3/smtp/email'
            headers = {
                'accept': 'application/json',
                'api-key': brevo_api_key.strip(),
                'content-type': 'application/json'
            }
            payload = {
                'sender': {'name': from_name, 'email': from_email},
                'to': [{'email': email} for email in recipient_emails],
                'subject': subject,
                'htmlContent': html_body,
                'textContent': plain_text
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode('utf-8'),
                headers=headers,
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                res_body = resp.read().decode('utf-8')
                print(f"[Ignite Email] Successfully sent via Brevo HTTPS API: {res_body}", flush=True)
                return
        except urllib.error.HTTPError as he:
            err_body = he.read().decode('utf-8', errors='ignore')
            print(f"[Ignite Email] Brevo HTTPS API error ({he.code}): {err_body}", flush=True)
        except Exception as e:
            print(f"[Ignite Email] Brevo HTTPS API exception: {e}", flush=True)

    try:
        print(f"[Ignite Email] Sending via SMTP to {recipient_emails}...", flush=True)
        msg = EmailMultiAlternatives(
            subject=subject,
            body=plain_text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipient_emails,
        )
        msg.attach_alternative(html_body, "text/html")
        sent = msg.send(fail_silently=False)
        print(f"[Ignite Email] Successfully sent confirmation email via SMTP (count={sent})", flush=True)
    except Exception as e:
        print(f"[Ignite Email] Failed to send confirmation email via SMTP: {e}", flush=True)


def get_registration_context(reg):
    college = 'Narsimha Reddy Engineering College (NRCM)'
    if reg.college_selection == 'OTHER' and reg.college_name_other:
        college = reg.college_name_other
    elif reg.college_selection == 'NRCM':
        college = 'Narsimha Reddy Engineering College (NRCM)'

    trans_id = reg.transaction_id if reg.transaction_id else (
        'Recorded (NRCM Student)' if reg.college_selection == 'NRCM' else 'Recorded'
    )

    return {
        'registration': reg,
        'team_name': reg.project_title,
        'project_title': reg.project_title,
        'team_size': reg.team_size,
        'team_leader_name': reg.team_leader_name,
        'theme': reg.project_category or 'Engineering Expo',
        'transaction_id': trans_id,
        'college': college,
        'members': list(reg.team_members.all()),
        'whatsapp_link': 'https://chat.whatsapp.com/DjPvw8V5RANCUzECRVVt80',
    }

def get_verified_registration(request):
    reg_id = request.session.get('registration_id')
    if not reg_id:
        return None
    try:
        from django.db import connection
        if connection.connection and connection.connection.closed:
            connection.connect()
        return Registration.objects.prefetch_related('team_members').filter(id=reg_id).first()
    except Exception:
        try:
            from django.db import connection
            connection.close()
            return Registration.objects.prefetch_related('team_members').filter(id=reg_id).first()
        except Exception:
            return None

def success(request):
    reg = get_verified_registration(request)
    if not reg:
        messages.error(request, "Access restricted: You must complete a successful registration to view this page.")
        return redirect('register')
    context = get_registration_context(reg)
    return render(request, 'web/registration_success.html', context)

def receipt(request):
    reg = get_verified_registration(request)
    if not reg:
        messages.error(request, "Access restricted: You must complete a successful registration to access your receipt.")
        return redirect('register')
    context = get_registration_context(reg)
    return render(request, 'web/registration_receipt.html', context)

def pdf_receipt(request):
    reg = get_verified_registration(request)
    if not reg:
        messages.error(request, "Access restricted: You must complete a successful registration to access your PDF receipt.")
        return redirect('register')
    context = get_registration_context(reg)
    return render(request, 'web/pdf_receipt.html', context)

from django.http import JsonResponse
from django.templatetags.static import static
from .models import GalleryImage

def gallery_api(request):
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
