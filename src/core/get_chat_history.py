import csv
import logging

from config.common import HISTORY_SAVE_DIRECTORY


def get_chat_history(chat_id: int, from_message_id: int):
    logger = logging.getLogger(__name__)
    
    messages = []
    file_name = f'{HISTORY_SAVE_DIRECTORY}/chat_history_{str(chat_id)}.csv'

    try:
        with open(file_name, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            
            # Skip header row
            header = next(reader, None)
            if header is None:
                logger.info(f"Chat history file {file_name} is empty")
                return []

            for row in reader:
                try:
                    if len(row) < 3:
                        logger.warning(f"Skipping invalid row with {len(row)} columns")
                        continue
                    
                    message_id = int(row[0])
                    sender = row[1]
                    message_text = row[2]
                    
                    # Unescape newlines that were escaped when saving
                    message_text = message_text.replace('\\n', '\n').replace('\\r', '\r')
                    
                    if message_id < from_message_id:
                        continue

                    messages.append({
                        "sender": sender,
                        "message": message_text
                    })
                    
                except (ValueError, IndexError) as e:
                    logger.warning(f"Skipping invalid row: {row}, error: {e}")
                    continue
                
    except FileNotFoundError:
        logger.info(f"Chat history file {file_name} doesn't exist yet")
        return []
    except Exception as e:
        logger.error(f"Error reading chat history file {file_name}: {e}")
        return []

    logger.info(f"Retrieved {len(messages)} messages from chat history")
    return messages
