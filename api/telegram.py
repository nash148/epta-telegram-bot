import json
from telegram import Update
from bot import create_application

app = create_application()

async def handler(request):
    if request.method != "POST":
        return {
            "statusCode": 405,
            "body": "Method Not Allowed"
        }

    try:
        update_data = json.loads(request.body)
        update = Update.de_json(update_data, app.bot)
        await app.process_update(update)
        return { "statusCode": 200, "body": "OK" }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Error: {str(e)}"
        }