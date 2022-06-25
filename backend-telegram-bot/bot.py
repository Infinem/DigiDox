import os
import telebot
import urllib
import cv2

from paddleocr import PaddleOCR

ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False)

TOKEN = "5365324529:AAEh99uv84P2UJQ_guz1pix4IvkQVpdlWpA"
bot = telebot.TeleBot(TOKEN)

 
def save_image_from_message(message):
    if not os.path.exists("./tmp"):
        os.makedirs("./tmp")
 
    if message.photo:
        image_id = message.photo[len(message.photo)-1].file_id
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
bot_text = """
Здравствуйте, меня зовут DigiDox! \U0001F642
 
Я бот который умеет находить и распознавать документы \U0001F44C
 
Принимаю фото\U0001F4F1 и сканы \U0001F5A8  хорошего качества
 
@digidox_bot
"""
 
@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.send_message(message.chat.id, bot_text)
 
@bot.message_handler(content_types=["photo", "document"])
def handle(message):
    eng_uzb_dict = {"GIVEN NAMES": "ISMI", "SURNAME": "FAMILIYASI", "SEX": "JINSI",
                    "DATE OF BIRTH": "TUG'ILGAN SANASI", "SERIAL": "PASPORT SERIYASI",
                    "NUMBER": "PASPORT RAQAMI", "DATE OF ISSUE": "BERILGAN SANASI",
                    "DATE OF EXPIRY": "AMAL QILISH MUDATTI", "GIVEN BY": "KIM TOMONIDAN BERILGAN",
                    "PINFL": "PINFL"}
    bot.send_message(message.chat.id, "Анализирую, ждите... \U0001F9D0")
    # try:
    path = save_image_from_message(message)
    # except:
    #     bot.send_message(message.chat.id, "Отправьте фото!")
    #     return None
    
    output = ""

    result = ocr.ocr(path, cls=True)

    image = cv2.imread(path)
    for item in result:
        xmin = int(min([p[0] for p in item[0]]))
        xmax = int(max([p[0] for p in item[0]]))
        ymin = int(min([p[1] for p in item[0]]))
        ymax = int(max([p[1] for p in item[0]]))
        cv2.rectangle(image, (xmin, ymax), (xmax, ymin), (0, 255, 0), 2)
        cv2.putText(image, item[1][0], (xmin, ymin), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.5, (0, 0, 255), 2, cv2.LINE_AA)
    cv2.imwrite("./tmp/result.jpg", image)

    bot.send_photo(message.chat.id, open('./tmp/result.jpg', "rb"), output)
    bot.send_message(message.chat.id, "Ура, я нашел! \U0001F929")
    # except:
    #     output = "Извините, ничего не нашел... \U0001F612\n\n" \
    #             + "Проверьте качество фотографии или скана."
    #     bot.send_photo(message.chat.id, open(path, "rb"), output)
    
    clean_tmp()
 
if __name__ == "__main__":
    bot.polling()