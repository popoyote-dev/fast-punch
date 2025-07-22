from flask import (
    Blueprint,
    current_app,
    render_template,
    request,
)
from services import QuestionService

router_configure = Blueprint("admin", __name__, url_prefix="/admin")
COFIG_TEMPLATE = "config.html"


@router_configure.get("/")
def config_index():
    serv: QuestionService = current_app.extensions["question_service"]

    return render_template(
        COFIG_TEMPLATE,
        status=serv.status,
        waiting=serv.remain_time,
        question_time=serv.QUESTION_TIME,
        score_time=serv.SCORE_TIME,
        players_time=serv.PLAYERS_TIME,
        total_questions=serv.TOTAL_QUESTIONS,
        is_show=False,
    )


@router_configure.get("/config")
def config():
    serv: QuestionService = current_app.extensions["question_service"]

    return render_template(
        COFIG_TEMPLATE,
        status=serv.status,
        waiting=serv.remain_time,
        question_time=serv.QUESTION_TIME,
        score_time=serv.SCORE_TIME,
        players_time=serv.PLAYERS_TIME,
        total_questions=serv.TOTAL_QUESTIONS,
        is_show=True,
    )


@router_configure.post("/config")
def config_post():
    serv: QuestionService = current_app.extensions["question_service"]

    total = int(request.form.get("total", 10))
    qtime = int(request.form.get("qtime", 30))
    stime = int(request.form.get("stime", 20))
    ptime = int(request.form.get("ptime", 10))

    serv.reset(total=total, qtime=qtime, stime=stime, ptime=ptime)

    return render_template(
        COFIG_TEMPLATE,
        status=serv.status,
        waiting=serv.remain_time,
        question_time=serv.QUESTION_TIME,
        score_time=serv.SCORE_TIME,
        players_time=serv.PLAYERS_TIME,
        total_questions=serv.TOTAL_QUESTIONS,
        is_show=False,
    )
