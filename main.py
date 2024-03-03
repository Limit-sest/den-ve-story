# TODO:
# https://blog.dennisokeeffe.com/blog/2021-07-20-python-unsplash
# Dát story do výběru
# Do budoucna: počasí a prázdniny/státní svátky

from PIL import Image, ImageOps, ImageFilter, ImageEnhance, ImageDraw, ImageFont
import os
import config
from random import randint
import requests
from datetime import datetime
from time import sleep
from pytz import timezone
from instagrapi import Client

cl = Client()
sessionID = None
try:
    import login_save
    username = login_save.username
    password = login_save.password
    sessionID = login_save.sessionID
except:
    username = input("Please enter your username: ")
    password = input("Please enter your password: ")
    sessionID_ask = input("Would you like to login with sessionID? (y/n):")
    if sessionID_ask.lower() == "y":
        sessionID = input("Please enter your sessionID:")
    save_ask = input("Would you like to save your credentials? (y/n): ")
    if save_ask.lower() == "y":
        try:
            f = open("login_save.py", "w")
            f.write(f'username = "{username}"\n')
            f.write(f'password = "{password}"\n')
            f.write(f'sessionID = "{sessionID}"\n')
            f.close()
        except Exception as e:
            print(f"Couldn't write to login file: {e}")
        else:
            print("Succesfully saved username & pasword")

if config.skip_ig != True:
    try:
        if sessionID and config.use_session_id:
            print("Trying to log in using sessionID")
            if cl.login_by_sessionid(sessionID):
                print(f"Logged in as {cl.username}")
            else:
                print(f"Couldn't log in (using sessionID): Unknown")
        else:
            if config.use_session_id:
                raise Exception("No sessionID provided.")
            else:
                raise Exception("SessionID login disabled in config.")
    except Exception as e:
        print(f"Couldn't log in (using sessionID): {e}")
        try:
            print("Trying to log in using username & password")
            if cl.login(username, password):
                print(f"Logged in as {cl.username}")
            else:
                print(f"Couldn't log in (using username & password): Unknown")
        except Exception as e:
            print(f"Couldn't log in (using username & password): {e}")

bg = Image.open("assets/bg.png")
bg2_files = []
name_font = ImageFont.truetype("assets/Cairo-Black.ttf", 150)
date_font = ImageFont.truetype("assets/Proxima Nova Extrabold.otf", 75)
text_font = ImageFont.truetype("assets/Proxima Nova Regular.otf", 50)

last_img_index = None

basepath = 'assets/bg2'
with os.scandir(basepath) as entries:
    for entry in entries:
        if entry.is_file():
            bg2_files.append(entry.path)

def round_corners(im, rad):
    circle = Image.new('L', (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2 - 1, rad * 2 - 1), fill=255)
    alpha = Image.new('L', im.size, 255)
    w, h = im.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    im.putalpha(alpha)
    return im

def add_text(im, text):
    last_coords = [(im.size[0] / 2),0]
    textbox_h = 0
    textbox_w = 0

    # Calculating size of image that the text will be on
    for i in range(len(text)):
        font = text[i][1]
        draw = ImageDraw.Draw(im)
        string = text[i][0]
        space_below = text[i][2]

        bbox = draw.textbbox(last_coords, string, font=font, anchor="mt")
        text_h = bbox[3] - bbox[1]
        text_w = bbox[2] - bbox[0]
        
        # Check for text overflow
        while text_w > im.size[0]/1.1:
            font = ImageFont.truetype(font.path, font.size - 2)
            bbox = draw.textbbox(last_coords, string, font=font, anchor="mt")
            text_w = bbox[2] - bbox[0]
        
        textbox_h += text_h + space_below
        if textbox_w < text_w:
            textbox_w = text_w


        last_coords[1] += text_h + space_below

    text_im = Image.new("RGBA", (int(textbox_w), int(textbox_h)), (0, 0, 0, 0))
    last_coords = [(text_im.size[0] / 2),0]

    # Add text to the text image
    for i in range(len(text)):
        font = text[i][1]
        draw = ImageDraw.Draw(text_im)
        string = text[i][0]
        space_below = text[i][2]

        bbox = draw.textbbox(last_coords, string, font=font, anchor="mt")
        text_h = bbox[3] - bbox[1]
        text_w = bbox[2] - bbox[0]

        # Check for text overflow
        while text_w > text_im.size[0]/1.1:
            font = ImageFont.truetype(font.path, font.size - 2)
            bbox = draw.textbbox(last_coords, string, font=font, anchor="mt")
            text_w = bbox[2] - bbox[0]
        
        draw.text(last_coords, string, fill="white", font=font, anchor="mt")

        last_coords[1] += text_h + space_below
    
    text_im = text_im.resize((im.size[0], im.size[0] * text_im.size[1] // text_im.size[0]), Image.LANCZOS)

    coords = (int((im.size[0]/2)-(text_im.size[0]/2)), int((im.size[1]/2.1)-(text_im.size[1]/2)))
    im.paste(text_im, coords, text_im)# Merge the images

    return im

def bg2_process(im, text, size=(600,660)):
    cropped = ImageOps.fit(im, size)
    blurred = cropped.filter(ImageFilter.GaussianBlur(10))
    brightness = ImageEnhance.Brightness(blurred)
    dark = brightness.enhance(0.6)
    rounded = round_corners(dark, 50)
    return add_text(rounded, text)

def img_gen(text):
    global last_img_index
    index = randint(0, len(bg2_files)-1)
    while index == last_img_index:
        index = randint(0, len(bg2_files)-1)
    bg2 = Image.open(bg2_files[index])
    last_img_index = index

    processed_bg2 = bg2_process(bg2, text)
    coords = (int((bg.size[0]/2)-(processed_bg2.size[0]/2)), int((bg.size[1]/2.1)-(processed_bg2.size[1]/2)))
    bg.paste(processed_bg2, coords, processed_bg2)# Merge the images
    return bg

def check_time():
    time = datetime.now(timezone('Europe/Prague'))
    if time.hour == 0:
        return True
    else:
        return False

def img_save_post():
    response = requests.get("https://svatkyapi.cz/api/day").json()
    svatek = response["name"]
    day_number = response["dayNumber"]
    day_week = response["dayInWeek"]
    day_week = day_week.capitalize()
    month = response["month"]["genitive"]

    text = [("Svátek má", text_font, 10),
    (svatek, name_font, 40),
    (f"{day_week} {day_number}. {month}", date_font, 0)]

    generated_img = img_gen(text)
    generated_img = generated_img.convert("RGB")
    generated_img.save(fp="current_img.jpg")
    if config.use_show: generated_img.show()
    
    if config.skip_ig != True:
        try:
            if config.random_delay: sleep(randint(config.random_delay_range[0], config.random_delay_range[1]))
            cl.photo_upload_to_story("current_img.jpg")
        except Exception as e:
            print(f"Couldn't upload story: {e}")
        else:
            print("New story uploaded succesfully")

if config.skip_sleep:
    img_save_post()
else:
    while True:
        if check_time():
            img_save_post()
        sleep(3600)#1 hour