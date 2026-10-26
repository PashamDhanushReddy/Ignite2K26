
import os
import django
from django.core.files import File

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ignite_project.settings')
django.setup()

from web.models import GalleryImage

image_paths = [
    "/home/varshith/.gemini/antigravity/brain/719264f0-ac35-492a-b980-0eca626379c7/uploaded_media_0_1769713524709.png",
    "/home/varshith/.gemini/antigravity/brain/719264f0-ac35-492a-b980-0eca626379c7/uploaded_media_1_1769713524709.png",
    "/home/varshith/.gemini/antigravity/brain/719264f0-ac35-492a-b980-0eca626379c7/uploaded_media_2_1769713524709.png",
    "/home/varshith/.gemini/antigravity/brain/719264f0-ac35-492a-b980-0eca626379c7/uploaded_media_3_1769713524709.png"
]


import cloudinary.uploader

for path in image_paths:
    if os.path.exists(path):
        name = os.path.basename(path)
        print(f"Uploading {name}...")
        try:
            # Upload directly
            result = cloudinary.uploader.upload(path)
            public_id = result.get('public_id')
            
            # Save model with public_id
            GalleryImage.objects.create(
                image=public_id,
                alt_text=f"Ignite Gallery {name}"
            )
            print(f"Uploaded {name} successfully (ID: {public_id})")
        except Exception as e:
            print(f"Failed to upload {name}: {e}")
    else:
        print(f"File not found: {path}")

print("Done loading images.")
