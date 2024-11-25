import face_recognition as fr
import numpy as np
import requests
from io import BytesIO
from PIL import Image
import base64
from django.core.cache import cache
from django.apps import apps
import concurrent.futures

# Cache key for storing face encodings
FACE_ENCODINGS_CACHE_KEY = 'face_encodings_cache'

def load_image_from_base64(base64_string):
    """Load an image from base64 string and convert it to a numpy array"""
    img_data = base64.b64decode(base64_string)
    img = Image.open(BytesIO(img_data))
    if img.mode != 'RGB':
        img = img.convert('RGB')
    return np.array(img)

def load_image_from_url(url):
    """Load an image from a URL and convert it to a numpy array"""
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    if img.mode != 'RGB':
        img = img.convert('RGB')
    return np.array(img)

def get_encoded_faces():
    """
    This function loads all user profile images and encodes their faces.
    Uses caching to avoid re-processing images unnecessarily.
    """
    # Try to get encoded faces from cache
    encoded = cache.get(FACE_ENCODINGS_CACHE_KEY)
    if encoded is not None:
        return encoded

    # If not in cache, process all faces
    encoded = {}
    # Get User model dynamically to avoid circular imports
    User = apps.get_model('api', 'User')
    qs = User.objects.all()

    for p in qs:
        encoding = None
        if p.profile_path:
            try:
                # Load face from Cloudinary URL
                face = load_image_from_url(p.profile_path.url)
                face_encodings = fr.face_encodings(face)
                if len(face_encodings) > 0:
                    encoding = face_encodings[0]
                else:
                    print("No face found in the image")
            except Exception as e:
                print(f"Error processing image for user {p.email}: {e}")

        if encoding is not None:
            # Convert numpy array to list for JSON serialization
            encoded[p.email] = encoding.tolist()

    # Store in cache for 1 hour (3600 seconds)
    cache.set(FACE_ENCODINGS_CACHE_KEY, encoded, 3600)
    return encoded

def invalidate_face_encodings_cache():
    """Invalidate the face encodings cache"""
    cache.delete(FACE_ENCODINGS_CACHE_KEY)

def classify_face_base64(base64_str):
    """
    This function takes a base64 image string and returns the name of the face it contains
    """
    faces = get_encoded_faces()
    # Convert stored list back to numpy array
    faces_encoded = [np.array(encoding) for encoding in faces.values()]
    known_face_names = list(faces.keys())

    try:
        img = load_image_from_base64(base64_str)
        face_locations = fr.face_locations(img)
        unknown_face_encodings = fr.face_encodings(img, face_locations)

        if not unknown_face_encodings:
            return False

        def process_face(face_encoding):
            matches = fr.compare_faces(faces_encoded, face_encoding)
            face_distances = fr.face_distance(faces_encoded, face_encoding)
            best_match_index = np.argmin(face_distances)
            return known_face_names[best_match_index] if matches[best_match_index] else "Unknown"

        # Use ThreadPoolExecutor for parallel processing
        with concurrent.futures.ThreadPoolExecutor() as executor:
            face_names = list(executor.map(process_face, unknown_face_encodings))

        return face_names[0] if face_names else False
    except Exception as e:
        print(f"Error in classify_face: {e}")
        return False

def classify_face(img_url):
    """
    This function takes an image URL as input and returns the name of the face it contains
    """
    faces = get_encoded_faces()
    # Convert stored list back to numpy array
    faces_encoded = [np.array(encoding) for encoding in faces.values()]
    known_face_names = list(faces.keys())

    try:
        img = load_image_from_url(img_url)
        face_locations = fr.face_locations(img)
        unknown_face_encodings = fr.face_encodings(img, face_locations)

        if not unknown_face_encodings:
            return False

        def process_face(face_encoding):
            matches = fr.compare_faces(faces_encoded, face_encoding)
            face_distances = fr.face_distance(faces_encoded, face_encoding)
            best_match_index = np.argmin(face_distances)
            return known_face_names[best_match_index] if matches[best_match_index] else "Unknown"

        # Use ThreadPoolExecutor for parallel processing
        with concurrent.futures.ThreadPoolExecutor() as executor:
            face_names = list(executor.map(process_face, unknown_face_encodings))

        return face_names[0] if face_names else False
    except Exception as e:
        print(f"Error in classify_face: {e}")
        return False
