import re
import logging
import asyncio
from typing import Annotated

logging.basicConfig(
    format='[%(asctime)s] %(levelname)s %(name)s - %(message)s', 
    level=logging.INFO
)

import uvicorn
from envparse import env
from varcache import Varcache
from fastapi import FastAPI, Request, Response, Depends, Body, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from telegram import constants
from telegram.ext import ApplicationBuilder, ExtBot
from telegram.error import BadRequest
from telegram.helpers import escape_markdown

env.read_envfile()

# Environment variables
APP_TOKEN = env.str('APP_TOKEN')
TELEGRAM_BOT_TOKEN = env.str('TELEGRAM_BOT_TOKEN')


# Get application description from README.md
with open('./README.md') as f:
    description = f.read()


# Define FastAPI application
app = FastAPI(
    title="NotifierAlexfomalhaut",
    description=description,
    version="0.1.2",
)

# Configure authorization with token
security = HTTPBearer()
CredentialsType = Annotated[HTTPAuthorizationCredentials, Depends(security)]

# Create Telegram bot
app.telegram_bot = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build().bot


@app.post("/notify", status_code=204)
async def notify_view(request: Request,
                      credentials: CredentialsType, 
                      body: str = Body(media_type='text/plain')):
    """
    It sends request body to all users subscribed to related Telegram bot.
    Body must be in Markdown format.
    """
    # Check credentials
    if credentials.credentials != APP_TOKEN:
        raise HTTPException(
            status_code=403, 
            detail="Invalid authorization token."
        )

    # Load chats
    vcache = Varcache(dirpath='./data')
    chats = vcache.load(name='chats', default=set)

    if chats:
        # Prepare async tasks to send notifications
        tasks = [
            send_to_chat(chat_id, body, request.app.telegram_bot)
            for chat_id in chats
        ]

        # Send notifications
        try:
            await asyncio.gather(*tasks)
        except BadRequest as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    return Response(status_code=204)


async def send_to_chat(chat_id: int, text: str, telegram_bot: ExtBot):
    """
    Coroutine to send text to the chat_id using telegram_bot.
    """
    safe_text = safe_markdown_v2(text)
    try:
        await telegram_bot.send_message(
            chat_id=chat_id, text=safe_text,
            parse_mode=constants.ParseMode.MARKDOWN_V2,
        )
    except BadRequest:
        logging.warning(safe_text)
        await telegram_bot.send_message(
            chat_id=chat_id, text=escape_markdown(safe_text, version=2),
            parse_mode=constants.ParseMode.MARKDOWN_V2,
        )


def safe_markdown_v2(text: str) -> str:
    """
    Prepare the text for ParseMode.MARKDOWN_V2.
    """
    result = ""

    parts = re.split(
        r'(?<!\\)((?:\\\\)*)```(?:(\w*)\n)?(.*?)(?<!\\)((?:\\\\)*)```',
        text, flags=re.DOTALL
    )

    for ix in range(0, len(parts) - 1, 5):
        result += _escape_block(parts[ix] + parts[ix + 1])
        if lang := parts[ix + 2]:
            result += f"```{lang}\n{parts[ix + 3] + parts[ix + 4]}```"
        else:
            result += f"```{parts[ix + 3] + parts[ix + 4]}```"

    result += _escape_block(parts[-1])

    return result


def _escape_special(text: str):
    text = re.sub(r'(?<!\\)((?:\\\\)*)([\.\-\+\#\!\(\)])', r'\1\\\2', text)
    text = re.sub(r'\[(.+?)\]\\\((.*?)\\\)', r'[\1](\2)', text)
    return text


def _escape_block(text: str) -> str:
    result = ""
    parts = re.split(r'(?<!\\)((?:\\\\)*)`(.*?)(?<!\\)((?:\\\\)*)`', text)
    for ix in range(0, len(parts) - 1, 4):
        result += _escape_special(parts[ix] + parts[ix + 1])
        result += f"`{parts[ix + 2] + parts[ix + 3]}`"
    result += _escape_special(parts[-1])
    return result


if __name__ == "__main__":
    # Run API service with Uvicorn
    uvicorn.run('__main__:app', 
                host=env.str('HOST', default='localhost'), 
                port=env.int('PORT', default=8000), 
                log_level='info')
