import json
import os
from openai import OpenAI

from config.openai_config import MODEL, SYSTEM_PROMPT


def summarize(messages):
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"Starting summarization with {len(messages)} messages")
    messages_json = json.dumps(messages, indent=4, ensure_ascii=False)
    
    api_key = os.getenv('OPENAI_API_KEY')
    base_url = os.getenv('OPENAI_BASE_URL', 'https://openrouter.ai/api/v1')
    
    logger.info(f"API Key exists: {bool(api_key)}")
    logger.info(f"Base URL: {base_url}")
    logger.info(f"Model: {MODEL}")
    
    if not api_key:
        yield "Error: OPENAI_API_KEY not found in environment variables. Please check your .env file."
        return
    
    # Initialize OpenAI client with OpenRouter configuration
    client = OpenAI(
        api_key=api_key,
        base_url=base_url
    )

    try:
        # Create a streaming completion request
        stream = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": messages_json}
            ],
            stream=True,
            temperature=0.7
        )

        response_content = ""
        
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                response_chunk = chunk.choices[0].delta.content
                response_content += response_chunk
                
                metadata = "\n\n---\n\n"
                
                # Check if this is the last chunk
                if chunk.choices[0].finish_reason is not None:
                    metadata += f"Model: {MODEL}\n"
                    # metadata += "Summary generated successfully."
                # else:
                #     metadata += "Generating summary... Please wait."
                
                yield response_content + metadata
                
    except Exception as e:
        yield f"An error occurred while generating the summary: {str(e)}"


def get_summary(messages):
    """Non-streaming version that returns the complete summary"""
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"Starting summarization with {len(messages)} messages")
    messages_json = json.dumps(messages, indent=4, ensure_ascii=False)
    
    api_key = os.getenv('OPENAI_API_KEY')
    base_url = os.getenv('OPENAI_BASE_URL', 'https://openrouter.ai/api/v1')
    
    logger.info(f"API Key exists: {bool(api_key)}")
    logger.info(f"Base URL: {base_url}")
    logger.info(f"Model: {MODEL}")
    
    if not api_key:
        raise Exception("OPENAI_API_KEY not found in environment variables")
    
    # Initialize OpenAI client with OpenRouter configuration
    client = OpenAI(
        api_key=api_key,
        base_url=base_url
    )

    # Create a non-streaming completion request with extra headers for OpenRouter
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": messages_json}
        ],
        stream=False,
        temperature=0.7,
        extra_headers={
            "HTTP-Referer": "https://github.com/dudynets/Telegram-Summarize-Bot",
            "X-Title": "Telegram Summarize Bot"
        }
    )

    # Get the summary content
    summary_content = response.choices[0].message.content
    
    # Get token information from usage
    input_tokens = 0
    output_tokens = 0
    total_tokens = 0
    
    if hasattr(response, 'usage') and response.usage:
        logger.info(f"Usage object: {response.usage}")
        
        if hasattr(response.usage, 'prompt_tokens'):
            input_tokens = response.usage.prompt_tokens
        if hasattr(response.usage, 'completion_tokens'):
            output_tokens = response.usage.completion_tokens
        if hasattr(response.usage, 'total_tokens'):
            total_tokens = response.usage.total_tokens
    
    # Add footer with message count and token info
    footer = f"\n---\nSố tin nhắn đã tóm tắt: {len(messages)}\nTokens: {total_tokens} = {input_tokens} input + {output_tokens} output"
    
    return summary_content + footer
