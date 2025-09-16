from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from telegram import Update
from dotenv import load_dotenv
import os
import logging

from core.get_chat_history import get_chat_history
from core.save_message import save_message
from core.summarize import get_summary

load_dotenv()

logging.basicConfig(format='\n%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


async def message_handler(update: Update, context: CallbackContext) -> None:
    """
    Save the message to the chat history.
    
    This function is called when the user sends a message.
    It saves the message to the chat history file.
    """
    
    logger.info("MESSAGE HANDLER CALLED!")  # Debug log to see if handler is triggered
    
    try:
        is_edited = update.edited_message is not None
        message = update.edited_message if is_edited else update.message


        logger.info(f"Received message: '{message.text}' from {message.from_user.full_name} in chat {message.chat_id}")
        
        save_message(message, is_edited)
        logger.info("Message saved successfully")
    except Exception as e:
        logger.error(f"Error in message handler: {e}")
        logger.exception("Full error details:")


async def summarize_handler(update: Update, context: CallbackContext) -> None:
    """
    Generate a summary of the chat history.

    This function is called when the user sends the /summary command.
    It retrieves the chat history and sends it to the summarization model.
    Then, it sends the generated summary to the chat.
    """

    logger.info("Summarize handler called!")

    if not update.message.reply_to_message:
        logger.info("No reply_to_message found")
        await update.message.reply_text("Please reply to a message with the /summarize command to get a brief summary of the messages sent after it.")
        return
    
    chat_id = update.message.chat_id
    from_message_id = update.message.reply_to_message.message_id

    try:
        messages = get_chat_history(chat_id, from_message_id)

        if not messages or len(messages) == 0:
            await update.message.reply_text("No messages found to summarize. Most likely bot was just added to the chat.")
            return
        
    except Exception:
        await update.message.reply_text("Something went wrong while trying to retrieve the chat history.")
        logger.exception("Error while trying to retrieve the chat history.")
        return

    #     # Send initial message in italic
    await update.message.reply_text("_Đã nhận tin nhắn, đang tóm tắt..._", parse_mode='Markdown')
    
    try:
        # Get the summary (not streaming)
        summary = get_summary(messages)
        
        # Send the summary as a separate message
        await update.message.reply_text(summary)
    except Exception as e:
        logger.error(f"Error during summarization: {e}")
        # Send error message in italic
        await update.message.reply_text("_Tóm tắt bị lỗi._", parse_mode='Markdown')


async def error_handler(update: Update, context: CallbackContext):
    """
    Log the error.

    This function is called when an error occurs.
    It logs the error to the console.
    """

    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    load_dotenv()
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Debug handler to see ALL updates
    async def debug_handler(update: Update, context: CallbackContext):
        logger.info(f"DEBUG: Received update: {update}")
        if update.message:
            logger.info(f"DEBUG: Message text: '{update.message.text}', chat: {update.message.chat_id}")
    
    # Handle commands first with higher priority, then non-command messages
    app.add_handler(CommandHandler("summarize", summarize_handler))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), message_handler))
    app.add_handler(MessageHandler(filters.ALL, debug_handler))  # Catch all other updates
    app.add_error_handler(error_handler)

    app.run_polling()

if __name__ == '__main__':
    main()
