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
from telegram.ext import ApplicationBuilder
from telegram.error import BadRequest

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
    version="0.1.0",
)

# Configure authorization with token
security = HTTPBearer()
CredentialsType = Annotated[HTTPAuthorizationCredentials, Depends(security)]

# Create Telegram bot
app.telegram_bot = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build().bot


@app.post("/notify")
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
            request.app.telegram_bot.send_message(
                chat_id=chat_id, text=body, 
                parse_mode=constants.ParseMode.MARKDOWN,
            ) for chat_id in chats
        ]

        # Send notifications
        try:
            await asyncio.gather(*tasks)
        except BadRequest as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    return Response(status_code=204)


if __name__ == "__main__":
    # Run API service with Uvicorn
    uvicorn.run('__main__:app', 
                host=env.str('HOST', default='localhost'), 
                port=env.int('PORT', default=8000), 
                log_level='info')
