# notifier-alexfomalhaut

This application provides an API to accept notifications and passes them to the related Telegram that is also served by the application.

To configure the application you need to register your Telegram bot getting its `TELEGRAM_BOT_TOKEN` and generate `APP_TOKEN` that protects unknown users to subscribe and unknown applications to notify. Both variables are required in the environment.

To send a notification, all it is necessary is to call `POST /notify` endpoint, passing the message in the body in Markdown format and `Authorization: Bearer <APP_TOKEN>` in header.

## Run in docker

Build command: `docker build . -t notifier-alexfomalhaut`

Test run command: `docker run -it --rm --name=notifier-alexfomalhaut-app -p 8001:8000 -v ./data:/app/data --env-file=.env notifier-alexfomalhaut`

Production run command:  `docker run -it --restart=always --name=notifier-alexfomalhaut-app -p 8001:8000 -v ./data:/app/data --env-file=.env -d notifier-alexfomalhaut`
