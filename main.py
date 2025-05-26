from bot import create_application

if __name__ == "__main__":
    app = create_application()
    print("Bot is running...")
    app.run_polling()