from http import HTTPStatus
from random import choice

from flask import (
    Blueprint,
    Response,
    current_app,
    make_response,
    redirect,
    render_template,
    render_template_string,
    request,
    session,
    url_for,
)
from model import Answer, Avatar, Player
from repository import PlayerRepository
from services import QuestionService
from tools.avatars import load_avatars
from tools.event_stream import EventStream, EventStreamTemplate

router = Blueprint("app", __name__)

INDEX_FUNC = "app.index"


@router.get("/")
def index():
    avatars = load_avatars(current_app.static_folder)
    avatar = choice(avatars) if avatars else ""
    if isinstance(avatar, Avatar):
        avatar = avatar.url

    return render_template(
        "index.html",
        avatar=avatar,
        avatars=avatars,
    )


@router.get("/avatars")
def avatars():
    avatars = load_avatars(current_app.static_folder)
    return render_template("components/avatar_galery.html", avatars=avatars)


@router.get("/logout")
def logout():
    session["player"] = None
    return redirect(url_for(INDEX_FUNC), HTTPStatus.SEE_OTHER)


@router.post("/register")
def register():
    player = Player(**dict(request.form))
    repo: PlayerRepository = current_app.extensions["repo"]
    serv: QuestionService = current_app.extensions["question_service"]
    serv.start()
    if repo.add_player(player) and serv.waiting_player():
        session["player"] = player.__hash__()
        return redirect(url_for("app.quizz"), HTTPStatus.SEE_OTHER)

    return redirect(url_for(INDEX_FUNC), HTTPStatus.SEE_OTHER)


@router.get("/quizz")
def quizz():
    if session.get("player") is None:
        return redirect(url_for(INDEX_FUNC), HTTPStatus.SEE_OTHER)

    repo: PlayerRepository = current_app.extensions["repo"]
    serv: QuestionService = current_app.extensions["question_service"]

    player = repo.get_player(session.get("player"))

    response = make_response(
        render_template("quizz.html", player=player, waiting=serv.remain_time)
    )
    response.headers["HX-Trigger"] = "player-info"

    return response


@router.get("/player-info")
def player_info():
    if session.get("player") is None:
        return render_template_string("")

    repo: PlayerRepository = current_app.extensions["repo"]
    player = repo.get_player(session.get("player"))

    return render_template("components/player_info.html", player=player)


@router.post("/answer")
def answer():
    if session.get("player") is None:
        return ""

    answer = Answer(**dict(request.form))

    serv: QuestionService = current_app.extensions["question_service"]
    question = serv.evaluate(session.get("player"), answer=answer)

    return render_template(
        "components/answer.html",
        answer=answer,
        question=question,
    )


@router.get("/events")
def events():
    player = False if session.get("player") is None else True
    serv: QuestionService = current_app.extensions["question_service"]
    app = current_app._get_current_object()

    if player:
        event_question = EventStreamTemplate(
            event="question",
            template="components/question.html",
            app=app,
        )
        serv.add_action(event_question.action_stream, event="question")

        event_ended = EventStream(event="end-game", template="")
        serv.add_action(event_ended.action_stream, event="end")

    event_score = EventStreamTemplate(
        event="question",
        template="components/score.html",
        app=app,
    )
    serv.add_action(event_score.action_stream, event="score")

    event_graphic = EventStreamTemplate(
        event="answer-graphic",
        template="components/answer_graphic.html",
        app=app,
    )
    serv.add_action(event_graphic.action_stream, event="graphic")

    def event_stream(player: bool = True):
        while True:
            if player:
                yield from event_question.stream()
                yield from event_ended.stream()
                yield from event_graphic.stream()
            yield from event_score.stream()

    return Response(event_stream(player=player), mimetype="text/event-stream")


@router.get("/score")
def score():
    return render_template("score.html")
