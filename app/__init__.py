from flask import Flask, redirect, request
from flask_cors import CORS
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

CORS(app)
Bootstrap(app)


@app.before_request
def _redirect_legacy_host():
    # Canonical host is menus.tigerapps.org; the old herokuapp.com URL redirects.
    if request.host.endswith(".herokuapp.com"):
        target = "https://menus.tigerapps.org" + request.full_path
        return redirect(target.rstrip("?"), code=301)

from app import views  # noqa
