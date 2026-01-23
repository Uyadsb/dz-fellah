"""
Image handling utilities for DZ-Fellah
Handles base64 image uploads and saves them to media directory
"""

import base64
import uuid
import os
from django.conf import settings


def save_base64_image(base64_string, folder='uploads'):
    """
    Save a base64 encoded image to the media directory.
    
    Args:
        base64_string: Base64 encoded image string (with or without data URI prefix)
        folder: Subdirectory within MEDIA_ROOT to save the image
        
    Returns:
        str: Relative path to the saved image (URL-friendly)
    """
    
    if not base64_string:
        return None
    
    # Extract base64 data if it has data URI prefix
    if ',' in base64_string:
        # Format: "data:image/png;base64,iVBORw0KG..."
        header, base64_data = base64_string.split(',', 1)
        
        # Extract file extension from header
        if 'image/jpeg' in header or 'image/jpg' in header:
            ext = 'jpg'
        elif 'image/png' in header:
            ext = 'png'
        elif 'image/gif' in header:
            ext = 'gif'
        elif 'image/webp' in header:
            ext = 'webp'
        else:
            ext = 'jpg'  # Default
    else:
        # No header, assume it's pure base64
        base64_data = base64_string
        ext = 'jpg'  # Default extension
    
    try:
        # Decode base64 to binary - FIXED!
        image_data = base64.b64decode(base64_data)
        
        # Generate unique filename
        filename = f"{uuid.uuid4().hex}.{ext}"
        
        # Create folder path
        folder_path = os.path.join(settings.MEDIA_ROOT, folder)
        os.makedirs(folder_path, exist_ok=True)
        
        # Full file path
        file_path = os.path.join(folder_path, filename)
        
        # Save file
        with open(file_path, 'wb') as f:
            f.write(image_data)
        
        # Return relative path (for database storage)
        relative_path = f"{folder}/{filename}"
        
        print(f"✅ Image saved: {relative_path}")  # Debug log
        
        return relative_path
        
    except Exception as e:
        print(f"❌ Error saving base64 image: {e}")
        import traceback
        traceback.print_exc()
        return None


def delete_image(image_path):
    """
    Delete an image file from the media directory.
    
    Args:
        image_path: Relative path to the image (e.g., 'avatars/abc123.png')
        
    Returns:
        bool: True if deleted successfully, False otherwise
    """
    
    if not image_path:
        return False
    
    try:
        full_path = os.path.join(settings.MEDIA_ROOT, image_path)
        
        if os.path.exists(full_path):
            os.remove(full_path)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error deleting image: {e}")
        return False


def get_image_url(image_path):
    """
    Convert a relative image path to a full URL.
    
    Args:
        image_path: Relative path to the image (e.g., 'avatars/abc123.png')
        
    Returns:
        str: Full URL to the image
    """
    
    if not image_path:
        return None
    
    # If already a full URL, return as-is
    if image_path.startswith('http://') or image_path.startswith('https://'):
        return image_path
    
    # Build URL using MEDIA_URL setting
    media_url = settings.MEDIA_URL
    if not media_url.endswith('/'):
        media_url += '/'
    
    return f"{media_url}{image_path}"