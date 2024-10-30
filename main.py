import logging
import os
from datetime import datetime
from flask import Flask
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from passlib.hash import sha256_crypt
from flask import url_for

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

GP_POINTS = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
SPRINT_POINTS = [9, 7, 6, 5, 4, 3, 2, 1]
RACES = ["Bahrain", "Saudi Arabia", "Australia" "Azerbaijan", "Miami", "Monaco",
         "Spain", "Canada", "Austria", "Great Britain", "Hungary", "Belgium",
         "Netherlands", "Italy", "Singapore", "Japan", "Qatar", "Austin", "Mexico",
         "Brazil", "Las Vegas", "Abu Dhabi"]

if __name__ == "__main__":
    app.run()


@app.route("/")
def index():
    """A function that renders the main page and passes in the needed times"""
    return render_template("index.html", simple_date=get_simple_date, datetime=get_datetime())


@app.route("/participants")
def participants():
    """A function that renders the participants page and passes the needed time"""
    return render_template("participants.html", datetime=get_datetime())


@app.route("/championships")
def championships():
    """A function that renders championships page and passes the needed time and lists"""
    return render_template("championships.html", datetime=get_datetime(),
                           gp_points=GP_POINTS, sprint_points=SPRINT_POINTS)


@app.route("/about")
def about():
    """A function that renders about page and passes the needed time and list"""
    return render_template("about.html", datetime=get_datetime(), races=RACES)


@app.route("/redirect/<name>")
def _redirect(name: str):
    """A function that controls redirects.
    If more special cases are needed, they can be easily added"""
    allowed = ["f1", "fia"]
    match name:
        case "verstappen_brazil_fined":
            return redirect("https://www.espn.com/f1/story/_/id/32620381/max-verstappen-fined" +
                            "50000-touching-title-rival-lewis-hamilton-car-sao-paulo-grand-prix")
        case _:
            if name in allowed:
                return redirect(f"https://www.{name}.com")
            flash("Redirect now allowed")
            return redirect(url_for("index"))


@app.route("/profile/reset-password", methods=["GET", "POST"])
def reset_password():
    if g.user:
        if request.method == "POST":
            new_password = request.form["new-password"]
            if not equals_old_password(new_password):
                if is_vulnerable(new_password):
                    flash("Part of password is considered vulnerable. Consider changing")
                    # in theory, the entire password could be considered compromised
                    # in practice, chances of entire password being unsafe with rules is small
                    # easy to add check for it, make this an elif
                    # make initial - if new_password is word - and flash appropriate message
                    # DONT FORGET TO BREAK AFTER FLASHING

                if complex_password(new_password):
                    change_pwd(new_password)
                    flash("Your password was changed successfully")
                    return redirect(url_for("profile"))

                flash("New password does not follow complexity rules")
            else:
                flash("New password is the same as old password")

        return render_template("reset-password.html", datetime=get_datetime())
    flash("You must be logged in first")
    return redirect(url_for("login"))


@app.route("/profile/edit", methods=["GET", "POST"])
def edit():
    if g.user:
        if request.method == "POST":
            name = request.form["name"]
            if name not in ("", session["name"]):
                change_name(name)

            return redirect(url_for("profile"))

        return render_template("edit-profile.html", datetime=get_datetime(), name=session["name"])

    flash("You cannot access this page because you are not logged in")
    return redirect(url_for("login"))


@app.route("/profile")
def profile():
    if g.user:
        return render_template("profile.html", datetime=get_datetime(), user=session["user"],
                               name=session["name"], avatar=AVATAR)

    flash("You cannot access this page because you're not logged in")
    return redirect(url_for("login"))


@app.before_request
def before_request():
    g.user = None

    if "user" in session:
        g.user = session["user"]


@app.route("/dropsession")
def dropsession():
    session.pop("user", None)
    session["logged-in"] = False
    return redirect(url_for("login"))


# login next


def get_simple_date() -> str:
    return datetime.now().strftime("%b. %d of %Y")


def get_datetime() -> str:
    return datetime.now().strftime("%b. %d,  %Y at %I:%M %p")
