from datetime import datetime
import os
import logging
from flask import Flask
from flask import flash
from flask import render_template
from flask import redirect
from flask import request, session, g, url_for
from passlib.hash import sha256_crypt

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename="references/info.log"
)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
app.secret_key = os.urandom(24)
IMG_FOLDER = os.path.join("static", "IMG")
app.config["UPLOAD_FOLDER"] = IMG_FOLDER
AVATAR = os.path.join(app.config["UPLOAD_FOLDER"], "avatar.png")
