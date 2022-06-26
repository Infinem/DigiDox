import os
import telebot
import urllib

from reader.ocr_rule import rule_based_ocr

TOKEN = "5365324529:AAEh99uv84P2UJQ_guz1pix4IvkQVpdlWpA"
bot = telebot.TeleBot(TOKEN)


def save_image_from_message(message):
    if not os.path.exists("./tmp"):
        os.makedirs("./tmp")
    if message.photo:
        image_id = message.photo[len(message.photo) - 1].file_id
        file_path = bot.get_file(image_id).file_path
    if message.document:
        raise
    image_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
    image_name = f"{image_id}.jpg"
    urllib.request.urlretrieve(image_url, f"./tmp/{image_name}")
    return os.path.join("./tmp/", image_name)


def clean_tmp():
    for f in os.listdir("./tmp/"):
        os.remove(f"./tmp/{f}")

# Telegram bot
bot_text_ru = """
Здравствуйте, меня зовут DigiDox! \U0001F642
 
Я бот который умеет находить и распознавать документы \U0001F44C
 
Принимаю фото\U0001F4F1 и сканы \U0001F5A8  хорошего качества
 
@digidox_bot
"""

# Telegram bot
bot_text_uz = """
Assalomu Alaykum, mening ismim DigiDox! \U0001F642
 
Men hujjatlardan ma'lumotlarni qidira olaman va so'zlarni taniy olaman \U0001F44C
 
Rasmlarni \U0001F4F1 yoki nusxalarni \U0001F5A8 yaxshi sifatda yuboring
 
@digidox_bot
"""

doc_type = ""

@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.send_message(message.chat.id, bot_text_uz)
    send_menu(message)


@bot.message_handler(content_types=["text"])
def send_menu(message):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton(text="Guvohnoma", callback_data="guvohnoma")
    )
    markup.add(
        telebot.types.InlineKeyboardButton(text="Passport", callback_data="passport")
    )
    markup.add(telebot.types.InlineKeyboardButton(text="ID", callback_data="id"))
    bot.send_message(message.chat.id, "Ma'lumot turi?", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def handle_query(query):
    global doc_type 
    doc_type = query.data
    if doc_type:
       bot.answer_callback_query(query.id)
       bot.send_message(query.message.chat.id, "Rasm yoki nusxa yuboring!")


@bot.message_handler(content_types=["photo", "document"])
def read_docs(message):
    global doc_type
    
    if not doc_type:
        bot.send_message(message.chat.id, "Boshlash uchun hujjat turini tanlang")
        send_menu(message)
        return None

    bot.send_message(message.chat.id, "Analiz qilyapman, kuting... \U0001F9D0")

    try:
        path = save_image_from_message(message)
    except:
        bot.send_message(message.chat.id, "Rasm yoki nusxa yuboring!")
        return None

    rule_based_ocr(path, doc_type)
    doc_type = ""
    
    # try:
    bot.send_photo(message.chat.id, open("./tmp/result.jpg", "rb"), "")
    bot.send_message(message.chat.id, "Topdim! \U0001F929")
    # except:
    #     output = "Uzur, aniqlay olmadim... \U0001F612\n\n" \
    #             + "Rasm sifatini tekshiring."
    #     bot.send_photo(message.chat.id, open(path, "rb"), output)
    clean_tmp()
    send_menu(message)
    

# if __name__ == "__main__":
#     bot.polling()
