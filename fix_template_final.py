import re

# Read the file
with open('dashboard/templates/dashboard/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix all split template tags
replacements = [
    # Domain filter
    (r'{% if filters\.project_category==category\s*\n\s*%}selected{% endif %}', 
     '{% if filters.project_category == category %}selected{% endif %}'),
    
    # Payment Status filter - pending
    (r"{% if filters\.selection_status=='pending' %}selected{%\s*\n\s*endif %}", 
     "{% if filters.selection_status == 'pending' %}selected{% endif %}"),
    
    # Payment Status filter - selected
    (r"{% if filters\.selection_status=='selected' %}selected{%\s*\n\s*endif %}", 
     "{% if filters.selection_status == 'selected' %}selected{% endif %}"),
    
    # Payment Status filter - rejected
    (r"{% if filters\.selection_status=='rejected' %}selected{%\s*\n\s*endif %}", 
     "{% if filters.selection_status == 'rejected' %}selected{% endif %}"),
    
    # Payment Status filter - waitlisted
    (r"{% if filters\.selection_status=='waitlisted'\s*\n\s*%}selected{% endif %}", 
     "{% if filters.selection_status == 'waitlisted' %}selected{% endif %}"),
    
    # Registration table - selected
    (r"{% if reg\.selection_status=='selected' %}selected{% endif\s*\n\s*%}", 
     "{% if reg.selection_status == 'selected' %}selected{% endif %}"),
    
    # Registration table - rejected
    (r"{% if reg\.selection_status=='rejected' %}selected{% endif\s*\n\s*%}", 
     "{% if reg.selection_status == 'rejected' %}selected{% endif %}"),
    
    # Registration table - waitlisted
    (r"{% if reg\.selection_status=='waitlisted' %}selected{%\s*\n\s*endif %}", 
     "{% if reg.selection_status == 'waitlisted' %}selected{% endif %}"),
]

for pattern, replacement in replacements:
    content = re.sub(pattern, replacement, content)

# Write back
with open('dashboard/templates/dashboard/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Fixed all split template tags")
