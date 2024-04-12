import os
import asyncio
import logging
import re
from difflib import SequenceMatcher
from telethon import TelegramClient, events
from telethon.tl.types import PhotoSize
from src.image_processor import process_image_for_ocr, IMAGES_DIR, clean_up_image, preprocess_image
from src.ocr_handler import extract_text, check_tesseract_installed, install_tesseract
from src.utilities import (
    generate_message_shortcut, get_or_request_credentials,
    compile_keywords_pattern, export_message_data, parse_group_input, get_list_of_recent_chats
)

# Setup logging
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(BASE_DIR, 'data', 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

LOG_FILE_PATH = os.path.join(LOGS_DIR, 'telegram_ocr.log')

def configure_logging():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    LOGS_DIR = os.path.join(BASE_DIR, 'data', 'logs')
    os.makedirs(LOGS_DIR, exist_ok=True)
    LOG_FILE_PATH = os.path.join(LOGS_DIR, 'telegram_ocr.log')

    # Clear all existing handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Set up detailed logging to file
    file_handler = logging.FileHandler(LOG_FILE_PATH, mode='a')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)

    # Define a console handler that only logs critical errors
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.CRITICAL)  # Change this if necessary to ERROR if critical logs are not enough
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)

    # Get root logger and configure it
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Capture everything by default
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

configure_logging()

def normalize_text(text):
    """ Normalize text by removing non-alphanumeric characters and converting to lower case. """
    return re.sub(r'\W+', '', text).lower()
def calculate_similarity(text, keywords):
    """Calculate the highest similarity score between text and any of the keywords."""
    normalized_text = normalize_text(text)
    highest_ratio = 0
    for keyword in keywords:
        normalized_keyword = normalize_text(keyword)
        sequence_matcher = SequenceMatcher(None, normalized_text, normalized_keyword)
        ratio = sequence_matcher.ratio()
        if ratio > highest_ratio:
            highest_ratio = ratio
    return highest_ratio



async def data_analysis(client, group_input, keywords, mode):
    chat_id = parse_group_input(group_input) if group_input else None
    pattern = compile_keywords_pattern(keywords) if keywords else None
    try:
        if chat_id:
            chat = await client.get_entity(chat_id)
            messages = await client.get_messages(chat, limit=100) if mode == 'h' else client.iter_messages(chat)
            for message in messages:
                await process_and_export_message(client, message, keywords, pattern)
        else:
            chats = await get_list_of_recent_chats(client)
            for chat in chats:
                messages = await client.get_messages(chat.id, limit=100) if mode == 'h' else client.iter_messages(chat.id)
                for message in messages:
                    await process_and_export_message(client, message, keywords, pattern)
    except Exception as e:
        logging.error(f"An error occurred during data analysis: {str(e)}")

# Assuming preprocess_image and process_image_for_ocr are synchronous functions:
async def process_and_export_message(client, message, keywords, pattern):
    if hasattr(message, 'photo') and message.photo:
        try:
            valid_sizes = [size for size in message.photo.sizes if isinstance(size, PhotoSize)]
            if not valid_sizes:
                logging.error("No valid photo sizes available.")
                return

            largest_photo = max(valid_sizes, key=lambda size: size.size)
            file_path = await client.download_media(message.media, file=os.path.join(IMAGES_DIR, f"{message.id}_{largest_photo.type}.jpg"))
            if file_path:
                processed_image_path = await process_image_for_ocr(file_path)
                if processed_image_path:
                    extracted_text = extract_text(processed_image_path)
                    if extracted_text and (not pattern or pattern.search(extracted_text)):
                        similarity = calculate_similarity(extracted_text, keywords) if keywords else None
                        message_data = {
                            'Message Time': str(message.date),
                            'Sender ID': message.sender_id,
                            'Text': extracted_text,
                            'Message ID': message.id,
                            'Chat ID': message.chat_id,
                            'Message Link': generate_message_shortcut(message),
                            'Local Image Path': processed_image_path,
                            'Accuracy': f"{similarity * 100:.2f}%" if similarity else "N/A"
                        }
                        await export_message_data(message_data, export_format='json')
                        # Image meets criteria, do not delete
                    else:
                        # Image does not meet criteria, delete both original and processed
                        await clean_up_image(processed_image_path)
                        await clean_up_image(file_path)
                        logging.info(f"Image and processed file removed due to insufficient text or keyword match: {processed_image_path}")
                else:
                    logging.error("Failed to process image for OCR.")
                    await clean_up_image(file_path)
            else:
                logging.error(f"Failed to download image for message {message.id}.")
        except Exception as e:
            logging.error(f"Failed to process image from message {message.id} due to error: {e}")
            await clean_up_image(file_path)  # Ensure cleanup even on failure


async def main():
    logging.info('Initializing Telegram OCR application...')
    if not check_tesseract_installed():
        if not install_tesseract():
            logging.error("Failed to install Tesseract OCR. Exiting...")
            return

    api_id, api_hash, phone_number = get_or_request_credentials()
    client = TelegramClient('anon', api_id, api_hash)
    await client.start(phone=phone_number)

    while True:
        mode = input("Choose mode - Historical (h) or Real-Time (r): ").lower()
        if mode in ['h', 'r']:
            group_input = input("Enter the Group ID or Link to scan: ")
            keywords = input("Enter keywords to filter by (comma-separated): ").split(',')
            print("Activity is logged, please check telegram_ocr.log for details.")
            await data_analysis(client, group_input, keywords, mode)
            break
        else:
            logging.error("Invalid mode selected. Please choose either 'Historical (h)' or 'Real-Time (r)'.")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
