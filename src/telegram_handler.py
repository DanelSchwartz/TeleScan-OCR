import re
import logging
from src.image_processor import process_image_for_ocr, clean_up_image
from src.ocr_handler import extract_text
from src.utilities import export_message_data, generate_message_shortcut

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


async def process_message_photo(message):
    """
    Downloads and processes a photo attached to a message, then extracts text.

    Parameters:
        message (Message): The Telegram message object containing a photo.

    Returns:
        str: The path to the processed image or None if processing fails.
    """
    try:
        img_path = await message.download_media()
        processed_image_path = process_image_for_ocr(img_path)
        return processed_image_path
    except Exception as e:
        logging.error(f"Error processing photo in message {message.id}: {e}")
        return None

def search_keywords_in_text(text, pattern):
    """
    Searches for compiled keywords pattern in the given text.

    Parameters:
        text (str): The text to search within.
        pattern (re.Pattern): The compiled regex pattern of keywords.

    Returns:
        bool: True if any keyword is found, False otherwise.
    """
    return bool(pattern.search(text)) if pattern else True

def construct_message_data(message, extracted_text):
    """
    Constructs a dictionary with relevant data extracted from a message.

    Parameters:
        message (Message): The Telegram message object.
        extracted_text (str): The text extracted from the message's attached photo.

    Returns:
        dict: A dictionary containing the extracted message data.
    """
    chat = message.chat if message.chat else None
    group_name = chat.title if chat else "Unknown"
    message_data = {
        "Message Time": str(message.date),
        "Sender ID": message.sender_id,
        "User NickName": getattr(message.sender, 'first_name', 'Unknown'),
        "UserName": getattr(message.sender, 'username', 'No Username'),
        "Message Text": extracted_text,
        "Group Sent From": group_name,
        "Message Shortcut": generate_message_shortcut(message)
    }
    return message_data

async def handle_message(message, pattern):
    """
    Process, extract, and optionally export data from a message containing a photo.

    Parameters:
        message (Message): The Telegram message to process.
        pattern (re.Pattern): The compiled regex pattern to filter extracted text.
    """
    try:
        processed_image_path = await process_message_photo(message)
        if processed_image_path:
            extracted_text = extract_text(processed_image_path)
            if extracted_text:
                if search_keywords_in_text(extracted_text, pattern):
                    message_data = construct_message_data(message, extracted_text)
                    export_message_data(message_data, export_format='json')
                else:
                    logging.info("No matching keywords found in extracted text.")
                clean_up_image(processed_image_path)
            else:
                logging.info("No text extracted from the image.")
        else:
            logging.error("Failed to process the image.")
    except Exception as e:
        logging.error(f"Error handling message {message.id}: {e}")