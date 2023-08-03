import os
import secrets
from flask import current_app
from PIL import Image

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_img(form_photo):
    if form_photo and allowed_file(form_photo.filename):
        random_hex = secrets.token_hex(8)
        _, f_ext = os.path.splitext(form_photo.filename)
        path = random_hex + f_ext
        picture_path = os.path.join(current_app.static_folder, 'post_pics', path)

        # Resize the image before saving
        image = Image.open(form_photo)
        image.thumbnail((625, 625))
        image.save(picture_path)

        return path
