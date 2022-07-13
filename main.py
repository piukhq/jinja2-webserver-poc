import base64
import datetime
from io import BytesIO
from wsgiref.simple_server import make_server

import falcon
import qrcode
from jinja2 import Template

mock_data = {
    "a0ada9c1-d581-4bc8-a007-a60ceee0ed79": {
        "account_number": "111111-222222-333333",
        "reward_code": "aaaaaa-bbbbbb-cccccc",
        "valid_until": datetime.date.today() + datetime.timedelta(days=1),
    },
    "69a6fd6b-d932-424e-b49e-cfdc08bc0166": {
        "account_number": "444444-555555-666666",
        "reward_code": "dddddd-eeeeee-ffffff",
        "valid_until": datetime.date.today() + datetime.timedelta(days=10),
    },
}

config = {
    "bink": {
        "title": "Bink!",
        "stylesheet": "bink.css",
        "how_to_use": [
            "Think about it",
            "Wait a while",
            "Action it",
            "Talk about it",
        ],
    },
    "jeffcorp": {
        "title": "JeffCorp Inc!",
        "stylesheet": "jeffcorp.css",
        "how_to_use": [
            "Eat some nachos",
            "Make some noise",
            "Fight a Penguin",
            "Beep Boop Doop",
        ],
    },
}


def _make_qr_code(reward_code):
    b = BytesIO()
    qrcode.make(reward_code).save(b)
    b.seek(0)
    return base64.b64encode(b.read()).decode()


class Index(object):
    def on_get(self, req, resp):
        slug = req.get_param("retailer_slug")
        reward_id = req.get_param("reward_id")
        account_number = mock_data[reward_id]["account_number"]
        reward_code = mock_data[reward_id]["reward_code"]
        valid_until = str(mock_data[reward_id]["valid_until"])
        with open("templates/base.css") as css:
            base_css = css.read()
        with open(f"templates/{slug}.css") as css:
            slug_css = css.read()
        css = str(base_css + slug_css).strip()
        with open("templates/index.html", "r") as f:
            t = Template(f.read()).render(
                css=css,
                title=config[slug]["title"],
                how_to_use=config[slug]["how_to_use"],
                account_number=account_number,
                reward_code=reward_code,
                valid_until=valid_until,
                reward_qr=_make_qr_code(reward_code),
            )
        resp.status = falcon.HTTP_200
        resp.content_type = "text/html"
        resp.text = t


class Healthz(object):
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.content_type = "text/plain"
        resp.text = "healthy"


app = falcon.App()
app.add_route("/", Index())
app.add_route("/healthz", Healthz())

if __name__ == "__main__":
    with make_server("", 6502, app) as httpd:
        print("Serving on port 6502...")
        httpd.serve_forever()
