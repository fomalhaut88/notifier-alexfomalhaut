# notifier-alexfomalhaut

This application provides an API to accept notifications and passes them to the related Telegram that is also served by the application.

To configure the application you need to register your Telegram bot getting its `TELEGRAM_BOT_TOKEN` and generate `APP_TOKEN` that protects unknown users to subscribe and unknown applications to notify. Both variables are required in the environment.

To send a notification, all it is necessary is to call `POST /notify` endpoint, passing the message in the body in Markdown format and `Authorization: Bearer <APP_TOKEN>` in header.

## Run in Docker

```
docker run \
    --restart=always \
    --name=notifier-alexfomalhaut-app \
    -p 8001:8000 \
    -v /var/lib/notifier-alexfomalhaut/data:/app/data \
    -e APP_TOKEN=uiwe3rai3xooh4eephah4Tu7iuGheajahvoh4hu7Xocoe5zah6aequohreghahr9 \
    -e TELEGRAM_BOT_TOKEN=7482936150:AAHk9mP2vXq7RjT4sNw8bLzF3cYdG6uE1aB \
    -d fomalhaut88/notifier-alexfomalhaut
```

Generate your own `APP_TOKEN` (by `pwgen 64`, for example) and use your `TELEGRAM_BOT_TOKEN` for the created Telegram Bot (via https://t.me/BotFather).

## Development

### `curl` example

```
curl -X POST https://notifier.alexfomalhaut.com/notify -H 'Authorization: Bearer ohGhoh9wee6IeV0Xahdae8eiRooY0Nid0phei5aongah0mooghe0ceR2Wah7li5a' -d 'Hey!!!'
```

Use your host instead of `https://notifier.alexfomalhaut.com` and `APP_TOKEN` instead of `ohGhoh9wee6IeV0Xahdae8eiRooY0Nid0phei5aongah0mooghe0ceR2Wah7li5a`. The message should be text.

### Docker Run

Build command: `docker build . -t notifier-alexfomalhaut`

Test run command: `docker run -it --rm --name=notifier-alexfomalhaut-app -p 8001:8000 -v ./data:/app/data --env-file=.env notifier-alexfomalhaut`

Production run command:  `docker run -it --restart=always --name=notifier-alexfomalhaut-app -p 8001:8000 -v ./data:/app/data --env-file=.env -d notifier-alexfomalhaut`
