import json
from os import listdir
from os.path import isfile, join

from repository import QuizzRepository


def load_files(repository: QuizzRepository, app_path: str) -> None:
    files = [
        f
        for f in listdir(app_path)
        if isfile(join(app_path, f)) and f.endswith(".json")
    ]
    for file in files:
        with open(join(app_path, file), "r", encoding="utf-8") as f:
            qs = f.read()
            repository.add_questions(json.loads(qs))
