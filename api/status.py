# status.py
def handler(request):
    return {
        "statusCode": 200,
        "headers": { "Content-Type": "text/html" },
        "body": "<h1>✅ EPTA Bot is running</h1><p>This means the server is deployed and responding.</p>"
    }