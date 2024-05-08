from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, CallbackQueryHandler, filters
from translate import Translator
from langdetect import detect


class LanguageBot:
    def __init__(self, api_token, channel_username):
        self.api_token = api_token
        self.channel_username = channel_username
        self.source_lang = ""
        self.target_lang = ""
        self.translator = None
        self.application = Application.builder().token(api_token).build()
        self.setup_handlers()

    def setup_handlers(self):
        self.application.add_handler(CommandHandler("start", self.select_lang))
        self.application.add_handler(CommandHandler("lang", self.select_lang))
        self.application.add_handler(CallbackQueryHandler(self.button))
        self.application.add_handler(MessageHandler(filters.TEXT, self.reply))

    async def select_lang(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.source_lang = detect(update.message.text)
        keyboard = [
            [
                InlineKeyboardButton("Russian", callback_data="ru"),
                InlineKeyboardButton("German", callback_data="de"),
                InlineKeyboardButton("Spanish", callback_data="es"),
                InlineKeyboardButton("French", callback_data="fr")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Select language:", reply_markup=reply_markup)

    async def button(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        self.target_lang = query.data.lower()
        self.translator = Translator(from_lang=self.source_lang, to_lang=self.target_lang)
        await query.answer()
        await query.edit_message_text(text=f"Translation target language set to {query.data}",
                                      reply_markup=InlineKeyboardMarkup([]))

    async def reply(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_input = update.message.text
        translation = self.translate(user_input)
        await update.message.reply_text(translation)

    def translate(self, text):
        if self.translator:
            return self.translator.translate(text)
        return "Translation language not set. Use /lang to set a language."

    async def fetch_translate_repost(self, chat_id):
        async for message in self.application.client.iter_history(self.channel_username):
            if message.text:
                translation = self.translate(message.text)
                await self.application.client.send_message(chat_id, translation)

    def run(self):
        self.application.run_polling()


if __name__ == '__main__':
    with open("api.txt", "r") as api_file:
        api_token = api_file.read().strip()
    channel_username = "CHAT-FOR-BOT-TESTING"  # Replace with your channel username
    bot = LanguageBot(api_token, channel_username)
    bot.run()
