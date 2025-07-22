from functools import cache
from os import listdir
from os.path import isfile, join

from flask import url_for
from model import Avatar

image_extensions = (".svg", ".png", ".jpeg", ".jpg")


@cache
def load_avatars(app_path: str) -> list[Avatar]:
    avatar_folder = "avatars"
    full_path = join(app_path, avatar_folder)

    return [
        Avatar(
            file=f"{avatar_folder}/{f}",
            url=url_for("static", filename=f"{avatar_folder}/{f}"),
        )
        for f in sorted(listdir(full_path))
        if isfile(join(full_path, f)) and f.endswith(image_extensions)
    ]
