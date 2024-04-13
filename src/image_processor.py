from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np
import os
import logging
import asyncio


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# Define the base directory correctly assuming this script resides in the 'src' directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Define the images directory and logs directory using the base directory
IMAGES_DIR = os.path.join(BASE_DIR, 'data', 'images')
LOGS_DIR = os.path.join(BASE_DIR, 'data', 'logs')

# Make sure that the directories exist
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Setup logging for image processing to use the correct logs directory
image_processing_log_path = os.path.join(LOGS_DIR, 'image_processing.log')
image_logger = logging.getLogger('image_processing')
image_logger.setLevel(logging.INFO)

# Check if the logger already has handlers set up
if not image_logger.hasHandlers():
    # Create a file handler for logging
    file_handler = logging.FileHandler(image_processing_log_path, mode='a')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
    file_handler.setFormatter(formatter)
    image_logger.addHandler(file_handler)
async def process_image_for_ocr(image_path):
    """
    Asynchronously enhances an image for better OCR results by converting it to grayscale,
    increasing contrast, and applying filters. Saves the processed image in a dedicated directory.
    """
    try:
        # Use asyncio to open the image asynchronously if available or run_in_executor for synchronous PIL methods
        loop = asyncio.get_event_loop()
        image = await loop.run_in_executor(None, Image.open, image_path)

        logger.info(f"Processing image for OCR: {image_path}")

        image = image.convert('L')
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        image = image.filter(ImageFilter.SHARPEN)

        processed_image_path = os.path.join(IMAGES_DIR, 'processed_' + os.path.basename(image_path))
        await loop.run_in_executor(None, image.save, processed_image_path)
        logger.info(f"Processed image saved: {processed_image_path}")

        return processed_image_path
    except Exception as e:
        logger.error(f"Failed to process image {image_path}: {e}")
        return None


def is_image_clear(image_path):
    """
    Determines if an image is clear and not blurry by calculating the variance
    of the Laplacian. Uses a predefined threshold to decide clarity.
    """
    try:
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            logger.error(f"Failed to load image for clarity check: {image_path}")
            return False

        laplacian_var = cv2.Laplacian(image, cv2.CV_64F).var()
        is_clear = laplacian_var > 50
        logger.info(f"Image clarity check for {image_path}: {'Clear' if is_clear else 'Blurry'}")
        return is_clear
    except Exception as e:
        logger.error(f"Error checking clarity of image {image_path}: {e}")
        return False
