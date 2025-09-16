import os
from dotenv import load_dotenv

# Load environment variables from .env file in the src directory
load_dotenv()

# Get model from environment variable (no fallback)
MODEL = os.getenv('OPENAI_MODEL')

START_SENTENCE = "Here is a summary of the chat messages sent after the message you replied to:"
SYSTEM_PROMPT = f"""
Bạn là một trợ lý AI hữu ích, người tóm tắt các tin nhắn trò chuyện.
Hãy cố gắng cung cấp một bản tóm tắt hữu ích về những gì đã được thảo luận trong các tin nhắn trò chuyện được cung cấp.
Trả lời bằng một đoạn văn tóm tắt những điểm chính của tin nhắn trò chuyện.
Bạn sẽ nhận được tin nhắn ở định dạng JSON hoặc CSV, nhưng đừng đề cập đến điều này trong phần tóm tắt.
"""
