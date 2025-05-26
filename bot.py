from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, KeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    ConversationHandler,
)
from openai import OpenAI
import os
from consts import (
    WELCOME_MESSAGE,
    CANCEL_COMMAND,
    CANCEL_MESSAGE,
    CONFIRMATION_START_BUTTON,
    QUESTIONS,
    FINISH_MESSAGE,
    ERROR_MESSAGE,
)


BOT_TOKEN = os.environ.get("BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

with open("system_prompt.txt", "r", encoding="utf-8") as f:
    system_prompt = f.read()

# Dictionary to store user responses
user_data = {}

(
    QUESTION_1,
    QUESTION_2,
    QUESTION_3,
    QUESTION_4,
    QUESTION_5,
    QUESTION_6,
    QUESTION_7,
    QUESTION_8,
    QUESTION_9,
    QUESTION_10,
) = range(10)


def get_keyboard(options):
    return ReplyKeyboardMarkup(
        [[opt] for opt in options], one_time_keyboard=True, resize_keyboard=True
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id] = {}
    context.user_data["state"] = 0
    user_full_name = update.effective_user.full_name
    await update.message.reply_text(
        WELCOME_MESSAGE.replace("{user_full_name}", user_full_name),
        reply_markup=get_keyboard([CONFIRMATION_START_BUTTON, CANCEL_COMMAND]),
    )
    return QUESTION_1


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(CANCEL_MESSAGE, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


async def question_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state = context.user_data["state"]

    questions = QUESTIONS

    if state > 0:  # skip first input (it's the start confirmation)
        user_data[user_id][f"answer_{state}"] = update.message.text

    if state < len(questions):
        context.user_data["state"] = state + 1
        q_text, options = questions[state]

        if options:
            await update.message.reply_text(q_text, reply_markup=get_keyboard(options))
        else:
            await update.message.reply_text(q_text, reply_markup=ReplyKeyboardRemove())
        return state + 1
    else:
        await update.message.reply_text(
            FINISH_MESSAGE, reply_markup=ReplyKeyboardRemove()
        )
        print(user_data[user_id])
        response = await process_with_openai(user_data[user_id])
        await update.message.reply_text(response)
        return ConversationHandler.END


async def process_with_openai(user_answers):
    content = "\n".join(
        [
            f"שאלה {i+1} - {QUESTIONS[i][0]}: {ans}"
            for i, ans in enumerate(user_answers.values())
        ]
    )
    
    try:
        response = client.chat.completions.create(
            model="gpt-4.1",  # or "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content},
            ],
        )
        print("Response: ", response)
        return response.choices[0].message.content
    except Exception as e:
        print("Error: ", e)
        return ERROR_MESSAGE.format(error=e)


# async def chat_with_gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user_message = update.message.text
#     print("User message: ", user_message)
#     response = client.chat.completions.create(
#         model="gpt-4o-mini",  # or "gpt-3.5-turbo"
#         messages=[
#             {
#                 "role": "system",
#                 "content": "Always start your responses with 'Hey EPTA!'",
#             },
#             {"role": "user", "content": user_message},
#         ],
#     )
#     print("Response: ", response)
#     reply = response.choices[0].message.content
#     await update.message.reply_text(reply)


def create_application():
    print("✅ Bot application is initializing...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            i: [MessageHandler(filters.TEXT & ~filters.COMMAND, question_handler)]
            for i in range(len(QUESTIONS) + 1)
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        name="epta_conversation",
    )

    app.add_handler(conv_handler)
    print("✅ Handlers registered successfully.")
    return app
