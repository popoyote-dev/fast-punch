import os
from uuid import uuid4

from flask import Flask
from repository import PlayerRepository, QuizzRepository
from services import QuestionService
from tools.load_default import load_files
from views.configure import router_configure
from views.game import router

APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TEMPL_DIR = os.path.join(APP_DIR, "templates")
STATIC_DIR = os.path.join(APP_DIR, "static")


def create_app() -> Flask:
    app = Flask("quizz", template_folder=TEMPL_DIR, static_folder=STATIC_DIR)
    app.secret_key = uuid4().hex

    quizz_repository = QuizzRepository()
    load_files(quizz_repository, os.path.join(APP_DIR, "data"))

    repo = PlayerRepository()
    app.extensions["repo"] = repo

    serv = QuestionService(players=repo, quizz=quizz_repository)
    serv.init_app(app)

    app.register_blueprint(router)
    app.register_blueprint(router_configure)

    return app
