"""
Image Preprocessing Utilities
Prepares raw images for model evaluation.
"""
from PIL import Image
import io

def preprocess_image(image_bytes: bytes, target_size=(224, 224)):
    """
    Resizes and normalizes raw byte streams into standard image dimensions.
    """
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image = image.resize(target_size)
    return image
