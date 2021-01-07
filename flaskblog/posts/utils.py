import os
import secrets

from flask import current_app


'''def save_img(form_photo):
    if form_photo:
        random_hex = secrets.token_hex(8)
        _, f_ext = os.path.splitext(form_photo.filename)
        path = random_hex + f_ext
        picture_path = os.path.join(current_app.root_path, 'static/post_pics', path)
        size = (625, 625)
        j = Image.open(form_photo)
        j.thumbnail(size)
        j.save(picture_path)
        return path
'''


def save_img(form_photo):
    if form_photo:
        random_hex = secrets.token_hex(8)
        _, f_ext = os.path.splitext(form_photo.filename)
        path = random_hex + f_ext
        picture_path = os.path.join(current_app.root_path, 'static/post_pics', path)
        size = (625, 625)
        form_photo.save(picture_path)

        return path