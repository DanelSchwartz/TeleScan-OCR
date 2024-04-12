import json
import csv
import os
import sys
import logging
from datetime import datetime
import re

# Setup basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE_PATH = os.path.join(BASE_DIR, 'config.ini')
LOGS_DIR = os.path.join(BASE_DIR, 'data', 'logs')
IMAGES_DIR = os.path.join(BASE_DIR, 'data', 'images')

# Ensure necessary directories exist
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

def parse_group_input(group_input):
    """Parses group input to handle different formats like numeric IDs or t.me links."""
    if group_input.isdigit():
        return int(group_input)  # It's a numeric ID.
    elif group_input.startswith('https://t.me/'):
        return group_input.split('https://t.me/')[1]  # Full link is provided.
    elif group_input.startswith('t.me/'):
        return group_input.split('t.me/')[1]  # Partial link is provided.
    else:
        return group_input  # Assume it's a valid username or chat ID.

async def get_list_of_recent_chats(client):
    """Fetches a list of recent chats from the Telegram client."""
    try:
        return await client.get_dialogs()
    except Exception as e:
        logging.error(f"Failed to fetch chat list: {e}")
        return []

def compile_keywords_pattern(keywords):
    """Compiles a regex pattern from a list of keywords."""
    if keywords:
        pattern_str = '|'.join(re.escape(keyword) for keyword in keywords)
        return re.compile(pattern_str, re.IGNORECASE)
    return None


async def export_message_data(data, export_format='json', filename_prefix='export'):
    if not data.get('Text'):  # Skip exporting if text is empty
        return

    filepath = os.path.join(LOGS_DIR, f'{filename_prefix}.{export_format}')

    # Handle each format
    if export_format == 'json':
        all_data = []

        # Load existing data if file exists
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as file:
                    all_data = json.load(file)
        except Exception as e:
            logging.error(f"Failed to load existing data: {e}")

        # Append new data and save
        all_data.append(data)
        with open(filepath, 'w', encoding='utf-8') as file:
            json.dump(all_data, file, ensure_ascii=False, indent=4)

    elif export_format == 'csv':
        try:
            write_header = not os.path.exists(filepath)
            with open(filepath, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=data.keys())
                if write_header:
                    writer.writeheader()
                writer.writerow(data)
        except IOError as e:
            logging.error(f"Error writing to CSV: {e}")

    elif export_format == 'txt':
        try:
            with open(filepath, 'a', encoding='utf-8') as f:
                for key, value in data.items():
                    f.write(f"{key}: {value}\n")
                f.write("\n")
        except IOError as e:
            logging.error(f"Error writing to TXT file: {e}")

    else:
        logging.error(f"Unsupported export format: {export_format}")

def export_to_csv(data, filename):
    """
    Writes provided data to a CSV file.

    Parameters:
        data (list of dicts): The data to write to the CSV.
        filename (str): The path where the CSV will be saved.
    """
    headers = data[0].keys() if data else []
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)
    logging.info(f"Data successfully exported to {filename}")


def export_to_txt(data, filename):
    """
    Writes provided data to a text file.

    Parameters:
        data (list of dicts): The data to write.
        filename (str): The path where the text file will be saved.
    """
    with open(filename, 'w', encoding='utf-8') as f:
        for item in data:
            for key, value in item.items():
                f.write(f"{key}: {value}\n")
            f.write("\n")
    logging.info(f"Data successfully exported to {filename}")


def export_to_json(logs, filepath):
    """
    Writes provided logs to a JSON file.

    Parameters:
        logs (dict or list): The log data to export.
        filepath (str): The filepath for the exported JSON.
    """
    with open(filepath, 'w', encoding='utf-8') as file:
        json.dump(logs, file, ensure_ascii=False, indent=4)
    logging.info(f"Logs successfully exported to {filepath}")

def generate_message_shortcut(message):
    """
    Generates a URL shortcut to access the specific message directly.

    Parameters:
        message (Message): The Telegram message object.

    Returns:
        str: The URL shortcut to the message.
    """
    chat_id = abs(message.chat.id)  # Using abs to handle negative IDs for groups
    message_id = message.id
    return f"https://t.me/c/{chat_id}/{message_id}"

def get_or_request_credentials():
    """
    Retrieves Telegram API credentials from environment variables or prompts the user.

    Returns:
        tuple: api_id, api_hash, phone_number
    """
    api_id = os.getenv('TELEGRAM_API_ID') or input("Enter your Telegram API ID: ")
    api_hash = os.getenv('TELEGRAM_API_HASH') or input("Enter your Telegram API Hash: ")
    phone_number = os.getenv('TELEGRAM_PHONE_NUMBER') or input("Enter your Telegram Phone Number: ")

    if not all([api_id, api_hash, phone_number]):
        logging.error("All API credentials must be provided.")
        sys.exit(1)

    return int(api_id), api_hash, phone_number
