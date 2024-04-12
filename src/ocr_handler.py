import pytesseract
from PIL import Image
import os
import subprocess
import sys
import logging
import configparser

# Setup basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

CONFIG_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.ini')
config = configparser.ConfigParser()

def check_tesseract_installed():
    """
    Checks if Tesseract OCR is installed and tries common paths if not found in the system path.
    """
    common_paths = [
        "C:\\Program Files\\Tesseract-OCR\\tesseract.exe",
        "C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe"
    ]

    # Check each path in the list
    for path in common_paths:
        if os.path.isfile(path) and os.access(path, os.X_OK):
            save_tesseract_path(path)
            return path

    # Ask user for the path if not found
    user_path = input("Please enter the path to the Tesseract executable or its directory: ").strip()
    if os.path.isdir(user_path):
        user_path = os.path.join(user_path, 'tesseract.exe')

    if os.path.isfile(user_path) and os.access(user_path, os.X_OK):
        save_tesseract_path(user_path)
        return user_path
    else:
        logging.error("Invalid path provided for Tesseract OCR. Please ensure Tesseract is installed and the path is correct.")
        sys.exit(1)

def save_tesseract_path(path):
    """
    Saves the provided Tesseract executable path to a configuration file.
    """
    config.read(CONFIG_FILE_PATH)
    config['Tesseract'] = {'Path': path}
    with open(CONFIG_FILE_PATH, 'w') as configfile:
        config.write(configfile)

def save_tesseract_path(path):
    """
    Saves the provided Tesseract executable path to a configuration file.
    """
    config.read(CONFIG_FILE_PATH)
    config['Tesseract'] = {'Path': path}
    with open(CONFIG_FILE_PATH, 'w') as configfile:
        config.write(configfile)

def install_tesseract():
    """
    Attempts to install Tesseract OCR based on the operating system.
    """
    os_name = platform.system()
    if os_name == "Windows":
        logging.info("Automatic installation of Tesseract OCR is not supported on Windows. Please download and install Tesseract from https://github.com/UB-Mannheim/tesseract/wiki.")
        sys.exit(1)
    elif os_name == "Linux":
        try:
            subprocess.run(["sudo", "apt", "install", "tesseract-ocr", "-y"], check=True)
            logging.info("Tesseract OCR installed successfully.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to install Tesseract OCR: {e}")
            sys.exit(1)
    elif os_name == "Darwin":
        try:
            subprocess.run(["brew", "install", "tesseract"], check=True)
            logging.info("Tesseract OCR installed successfully.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to install Tesseract OCR: {e}")
            sys.exit(1)
    else:
        logging.info("Automatic installation on this OS is not supported. Please install Tesseract OCR manually.")
        sys.exit(1)



# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')


# Configure the path to the Tesseract executable based on the system's configuration
tesseract_path = check_tesseract_installed()
if tesseract_path != "tesseract":
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

def extract_text(image_path, languages='eng+heb+ara+rus'):
    """
    Extracts text from an image using OCR, supporting multiple languages.

    Parameters:
        image_path (str): The path to the image from which to extract text.
        languages (str): The languages to use for OCR, formatted as Tesseract language codes separated by '+'.

    Returns:
        str: The extracted text, stripped of leading and trailing whitespace.
    """
    try:
        with Image.open(image_path) as img:
            logging.info(f"Starting OCR processing for {image_path}")
            text = pytesseract.image_to_string(img, lang=languages)
            cleaned_text = text.strip()
            logging.info(f"OCR processing completed for {image_path}")
            return cleaned_text
    except IOError:
        logging.error(f"Could not open the image at {image_path}.")
        return ""
    except Exception as e:  # General exception to catch any error from pytesseract
        logging.error(f"OCR processing error for {image_path}: {e}")
        return ""

