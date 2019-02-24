import flask


def create_changeip_response(tor_ip_changer):
    new_ip = ""
    error = ""
    status = 200

    try:
        new_ip = tor_ip_changer.get_new_ip()
    except Exception as exc:
        error = f"{exc.__class__}: {str(exc)}"
        status = 500

    response = flask.jsonify({"newIp": new_ip, "error": error})
    response.status_code = status

    return response, status


def init_server(tor_ip_changer):
    app = flask.Flask(__name__)

    @app.route("/")
    def index():
        return "TorIpChanger Server"

    @app.route("/changeip/")
    def changeip():
        return create_changeip_response(tor_ip_changer)

    return app
