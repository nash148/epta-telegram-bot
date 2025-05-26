# import json
# from telegram import Update
# from bot import create_application

# app = create_application()

# async def handler(request):
#     print(f"📩 Incoming request: {request.method}")
#     if request.method != "POST":
#         return {
#             "statusCode": 405,
#             "body": "Method Not Allowed"
#         }

#     try:
#         body = json.loads(request.body)
#         print(f"📦 Payload received: {body}")
#         update = Update.de_json(body, app.bot)
#         await app.process_update(update)
#         print("✅ Update processed successfully.")
#         return {"statusCode": 200, "body": "OK"}
#     except Exception as e:
#         print(f"❌ Error occurred: {e}")
#         return {
#             "statusCode": 500,
#             "body": f"Error: {str(e)}"
#         }

def handler(request):
    return {
        "statusCode": 200,
        "body": "Webhook received!"
    }