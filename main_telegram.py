from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import uuid
import requests
import pywhatkit as kt
import os
import telebot
import time
# from telebot import types
from dotenv import load_dotenv
from art import text2art
load_dotenv()
token = os.getenv('TOKEN')
me = os.getenv('ME')
bot = telebot.TeleBot(token)

media_folder = 'media'
os.makedirs(media_folder, exist_ok=True)

random_filename = str(uuid.uuid4())


def timer(message):
    # Wait for one hour (3600 seconds)
    time.sleep(10)


def delete_message_message(message):
    for i in range(0, 1):
        bot.delete_message(message.chat.id, message.message_id-i)


@bot.message_handler(commands=["start"])
def check_system(message):
    user_id = message.from_user.id
    bot.send_message(user_id, '```\nprint("Hello! Send me a photo")\n```',
                     parse_mode='MarkdownV2')
    image_hint = "nori.png"
    response = '```\n# hint\n```' + '```\nprint("It is better to upload simple photos:")\n```'
    file_hint = open('./' + image_hint, 'rb')
    bot.send_photo(message.chat.id, file_hint, caption=response, parse_mode='MarkdownV2')
    wait_for_photo(message)
    delete_message_message(message)


@bot.message_handler(commands=["photo"])
def wait_for_photo(message):
    user_id = message.from_user.id
    if message and message.photo:
        # Get the file ID of the latest photo
        file_id = message.photo[-1].file_id

        # Get the file information for the specific file ID
        photo_info = bot.get_file(file_id)

        file_url_zip = 'https://api.telegram.org/file/bot'
        file_url = f'{file_url_zip}{token}/{photo_info.file_path}'

        # Download the photo
        response = requests.get(file_url)

        photo_path = f"{media_folder}/{user_id}_{random_filename}.jpg"
        with open(photo_path, 'wb') as f:
            f.write(response.content)

        # Send a message to confirm the photo download
        bot.send_message(user_id, '```\nprint("proccesing!")\n```',
                         parse_mode='MarkdownV2')

        output_file_path_1 = f"{media_folder}/ascii_{random_filename}"
        kt.image_to_ascii_art(photo_path, output_file_path_1)

        with open(output_file_path_1 + '.txt', "r") as file:
            output_file_path_1 = file.read()
        text_content = f"""
        {output_file_path_1}
        Made by < leo >.
        """
        output_image_path_2 = f"{media_folder}/output_{random_filename}.png"
        text_to_image(text_content, output_image_path_2, contrast_factor=1.5)
        image = output_image_path_2
        file = open('./' + image, 'rb')
        bot.send_photo(message.chat.id, file)
        bot.send_message(user_id, '```\nprint("done, can send another!")\n```',
                         parse_mode='MarkdownV2')
    else:
        time.sleep(5)
        # bot.reply_to(message, "No photo found in the message."
        # "Please send a photo.")


def text_to_image(input_text, output_image_path, contrast_factor=1.5):
    # Set the image size based on the text length and font size
    font_size = 14
    lines = input_text.strip().split('\n')
    max_line_length = max(len(line) for line in lines)
    image_width = max_line_length * font_size
    image_height = len(lines) * font_size

    # Create a new image
    image = Image.new('RGB', (image_width, image_height), color='white')
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("monospace.medium.ttf", font_size)

    # Draw the text on the image
    y_position = 0
    for line in lines:
        draw.text((0, y_position), line, font=font, fill='blue')
        y_position += font_size

    enhancer = ImageEnhance.Contrast(image)
    image_with_contrast = enhancer.enhance(contrast_factor)
    # Save the image
    image_with_contrast.save(output_image_path)


@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    # Call the wait_for_photo function
    wait_for_photo(message)


@bot.message_handler(commands=["text"])
def wait_text(message):
    user_id = message.from_user.id
    bot.send_message(user_id, '```\nprint("Hello! Send me a text")\n```',
                     parse_mode='MarkdownV2')
    response = '```\n# hint\n```' + '```\nprint("keep it short")\n```'
    bot.send_message(user_id, response,
                     parse_mode='MarkdownV2')
    bot.register_next_step_handler(message, send_text)


def send_text(message):
    user_id = message.from_user.id
    user_input = message.text.strip().lower()
    ascii_art = text2art(user_input)

    output_image_path_3 = f"{media_folder}/text_output_{random_filename}.png"
    text_to_image(ascii_art, output_image_path_3, contrast_factor=1.5)
    image = output_image_path_3
    file = open('./' + image, 'rb')
    bot.send_photo(message.chat.id, file)
    bot.send_message(user_id, '```\nprint("done!")\n```',
                     parse_mode='MarkdownV2')


bot.infinity_polling(timeout=10, long_polling_timeout=5)
bot.polling(none_stop=True)
