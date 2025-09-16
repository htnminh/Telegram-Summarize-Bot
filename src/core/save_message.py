import csv
import os
import logging
from telegram import Message

from config.common import HISTORY_SAVE_DIRECTORY

logger = logging.getLogger(__name__)


def save_message(message: Message, is_edited: bool):
    chat_id = message.chat_id
    message_id = message.message_id
    sender = message.from_user.full_name
    message_text = message.text

    logger.info(f"HISTORY_SAVE_DIRECTORY: {HISTORY_SAVE_DIRECTORY}")
    file_name = f'{HISTORY_SAVE_DIRECTORY}/chat_history_{str(chat_id)}.csv'
    logger.info(f"Trying to save to: {file_name}")
    
    try:
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        logger.info(f"Directory created/verified: {os.path.dirname(file_name)}")
    except Exception as e:
        logger.error(f"Error creating directory: {e}")
        raise

    # Clean message text for CSV (escape quotes and newlines)
    clean_message = message_text.replace('\n', '\\n').replace('\r', '\\r') if message_text else ''

    try:
        # Check if file exists and has content
        file_exists = os.path.exists(file_name) and os.path.getsize(file_name) > 0
        
        if is_edited:
            # For edited messages, we need to update existing row
            update_message_in_csv(file_name, message_id, sender, clean_message, file_exists)
        else:
            # For new messages, just append
            with open(file_name, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
                
                # Write header if file is new
                if not file_exists:
                    writer.writerow(['message_id', 'sender', 'message'])
                
                writer.writerow([message_id, sender, clean_message])
                
        logger.info("Message saved successfully to CSV")
        
    except Exception as e:
        logger.error(f"Error saving message to CSV: {e}")
        raise


def update_message_in_csv(file_name, message_id, sender, message_text, file_exists):
    """Update an existing message in the CSV file"""
    if not file_exists:
        # File doesn't exist, create it with the message
        with open(file_name, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
            writer.writerow(['message_id', 'sender', 'message'])
            writer.writerow([message_id, sender, message_text])
        return

    # Read all rows, update the matching one
    rows = []
    updated = False
    
    try:
        with open(file_name, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) >= 3 and row[0] != 'message_id' and int(row[0]) == message_id:
                    # Update this row
                    rows.append([message_id, sender, message_text])
                    updated = True
                else:
                    rows.append(row)
    except Exception as e:
        logger.error(f"Error reading CSV for update: {e}")
        return

    # If message wasn't found, append it
    if not updated:
        rows.append([message_id, sender, message_text])

    # Write back all rows
    try:
        with open(file_name, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
            for row in rows:
                writer.writerow(row)
    except Exception as e:
        logger.error(f"Error writing updated CSV: {e}")
        raise
