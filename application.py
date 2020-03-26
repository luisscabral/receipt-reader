import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, send_from_directory, url_for
from flask_session import Session
from flask_dropzone import Dropzone
from flask_debugtoolbar import DebugToolbarExtension
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

import pytesseract
from pytesseract import Output
# from PIL import Image
from googletrans import Translator
import datetime
from datetime import date
from dateutil.parser import parse
import cv2
import re

from helpers import apology, login_required, lookup, usd, eur

UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = set(['bmp', 'pdf', 'png', 'jpg', 'jpeg'])

# Configure application
app = Flask(__name__)
dropzone = Dropzone(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Ensure templates are auto-reloaded
# app.config["TEMPLATES_AUTO_RELOAD"] = True

#-------------------
# DEBUGGING START
app.debug = True

# Enable flask session cookies
app.config['SECRET_KEY'] = 'key'

toolbar = DebugToolbarExtension(app)

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
# DEBUGGING END
#------------------

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd
app.jinja_env.filters["eur"] = eur

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///receipt.db")

most_common_passwords = [
    "123456",
    "123456789",
    "qwerty",
    "password",
    "1234567",
    "12345678",
    "12345",
    "iloveyou",
    "1111111",
    "123123"
]

categories = [
    "Clothes",
    "Drinks",
    "Entertainment",
    "Food",
    "Material",
    "Stay",
    "Transportation",
    "Utilities",
    "Other"
]

languages = [
    "eng",
    "deu",
    "fra",
    "ita",
    "nld",
    "por",    
    "spa",
]

def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        if request.form.get("action") == "export":
            return apology("TO DO", 400)
        else:
            return apology("TO DO", 400)
    else:
        """Show existing receipts"""
        total = 0
        receipts = db.execute("SELECT id, name, header, total, date, date_created, category, language, image_link FROM 'receipts' WHERE user_id = :user_id AND deleted = 0", user_id=session["user_id"])
        if receipts == []:
            return render_template("index_empty.html")
        else:
            for receipt in receipts:
                total =+ receipt["total"]
            return render_template("index.html", receipts = receipts, total = total)

@app.route("/about")
def about():
    """Describe the project"""
    return render_template("about.html")

@app.route("/edit", methods=["GET", "POST"])
@login_required
def edit(image, header, name, total, datetime, category, language):
    if request.method == "POST":
        if request.form.get("action") == "submit-edited":
            edit_image = image
            edit_header = request.form.get("header")
            edit_name = request.form.get("name")
            edit_total = request.form.get("total")
            edit_datetime = request.form.get("datetime")
            edit_category = request.form.get("category")
            edit_language = request.form.get("language")
            db.execute("INSERT INTO 'receipts' (user_id, header, name, total, date, date_created, category, language, image_link) VALUES (:user_id, :header, :name, :total, :date, :date_created, :category, :language, :image_link)", user_id = session["user_id"], header = edit_header, name = edit_name, total = float(edit_total), date = edit_datetime, date_created = date.today().strftime("%Y-%m-%d"), category = edit_category, language = edit_language, image_link = edit_image)
            db.execute("UPDATE users SET receipts = receipts + 1 WHERE id = :user_id", user_id = session["user_id"])
            flash("Saved!")
            return redirect("/")
        else:
            return render_template("edit.html", image = UPLOAD_FOLDER + filename, header = header, name = name, total = total, date_now = date.today().strftime("%Y-%m-%d"), datetime = datetime, category = category, language = language, categories = categories, languages = languages)
    else:
        #NOT REACHING HERE
        return render_template("edit.html", image = UPLOAD_FOLDER + filename, header = header, name = name, total = total, date_now = date.today().strftime("%Y-%m-%d"), datetime = datetime, category = category, language = language, categories = categories, languages = languages)


@app.route("/history")
@login_required
def history():
    """Show history of scans"""
    receipts = db.execute("SELECT id, name, header, total, date, date_created, category, language, image_link, deleted FROM 'receipts' WHERE user_id = :user_id", user_id=session["user_id"])
    if receipts == []:
        return render_template("history_empty.html")
    else:
        return render_template("history.html", receipts = receipts)
    return apology("TO DO")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide a username", 400)
        elif not request.form.get("password"):
            return apology("must provide a password", 400)
        elif request.form.get("password") in most_common_passwords:
            return apology("password not allowed because it belongs to most common passwords (according to wikipedia 2019)", 400)
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("password and confirmation must match", 400)
        else:
            password_hash = generate_password_hash(request.form.get("password"))
            new_user = db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)", username=request.form.get("username"), hash=password_hash)
            if not new_user:
                return apology("username already exists", 400)

            session["user_id"] = new_user
            flash("Registered!")
            return redirect("/")

    else:
        return render_template("register.html")

@app.route("/remove", methods=["GET", "POST"])
@login_required
def remove():
    if request.method == "POST":
        if request.form.get("remove"):
            receipt_id = request.form.get("remove")
            db.execute("UPDATE receipts SET deleted = 1 WHERE id = :receipt_id", receipt_id = receipt_id)
            flash("Removed!")
            return redirect("/")
        else:
            return redirect("/")
    else:
        #NOT REACHING HERE
        return redirect("/")


@app.route("/restore", methods=["GET", "POST"])
@login_required
def restore():
    if request.method == "POST":
        if request.form.get("restore"):
            receipt_id = request.form.get("restore")
            db.execute("UPDATE receipts SET deleted = 0 WHERE id = :receipt_id", receipt_id = receipt_id)
            flash("Restored!")
            return history()
        else:
            print(request.form)
            return history()
    else:
        #NOT REACHING HERE
        return redirect("/")


@app.route("/results", methods=["GET", "POST"])
@login_required
def results():
    if request.method == "POST":
        if request.form.get("action") == "edit":
            return edit(image = UPLOAD_FOLDER + filename, header = header, name = name, total = total, datetime = datetime, category = category, language = language)
        elif request.form.get("action") == "submit-edited":
            edit_header = request.form.get("header")
            edit_name = request.form.get("name")
            edit_total = request.form.get("total")
            edit_datetime = request.form.get("datetime")
            edit_category = request.form.get("category")
            edit_language = request.form.get("language")
            db.execute("INSERT INTO 'receipts' (user_id, header, name, total, date, date_created, category, language, image_link) VALUES (:user_id, :header, :name, :total, :date, :date_created, :category, :language, :image_link)", user_id = session["user_id"], header = edit_header, name = edit_name, total = float(edit_total), date = edit_datetime, date_created = date.today().strftime("%Y-%m-%d"), category = edit_category, language = edit_language, image_link = UPLOAD_FOLDER + image.filename)
            db.execute("UPDATE users SET receipts = receipts + 1 WHERE id = :user_id", user_id = session["user_id"])
            flash("Saved!")
            return redirect("/")
        else:
            db.execute("INSERT INTO 'receipts' (user_id, header, name, total, date, date_created, category, language, image_link) VALUES (:user_id, :header, :name, :total, :date, :date_created, :category, :language, :image_link)", user_id = session["user_id"], header = header, name = name, total = float(total), date = datetime, date_created = date.today().strftime("%Y-%m-%d"), category = category, language = language, image_link = UPLOAD_FOLDER + filename)
            db.execute("UPDATE users SET receipts = receipts + 1 WHERE id = :user_id", user_id = session["user_id"])
            flash("Saved!")
            return redirect("/")
    else:
        return render_template("results.html")


@app.route("/scan", methods=["GET", "POST"])
@login_required
def scan():
    """Scan a new receipt"""
    if request.method == "POST":
        global name
        name = request.form.get("name")
        if not name:
            return apology("you must name your receipt", 400)
        global category
        category = request.form.get("category")
        global language 
        language = request.form.get("language")
        global total_word
        total_word = "total"
        global image
        image = None
        if language != 'eng':
            total_word = Translator.translate(total_word, src= language)
        
        if not request.files["receipt-image"]:
            return apology("you must upload an image", 400)
        else: 
            image = request.files["receipt-image"]
        if not image or image.filename == '':
            return apology("you must upload an image", 400)
        elif not allowed_file(image.filename):
            return apology("file name is not allowed", 400)
        else:
            global datetime
            datetime = None
            global total
            total = None
            global filename 
            filename = secure_filename(image.filename) # add the time of creation of document
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            global img
            img = cv2.imread(UPLOAD_FOLDER + filename)
            global text
            text = pytesseract.image_to_string(img, lang= language)
            print(text)
            global text_lines
            text_lines = text.split("\n")
            global header
            header = "{} {}".format(text_lines[0], text_lines[1])
            global text_dict
            text_dict = pytesseract.image_to_data(img, lang= language, output_type=Output.DICT)
            global n_boxes
            n_boxes = len(text_dict['level'])
            global overlay
            overlay = img.copy()
            for i in range(n_boxes):
                lookfor = text_dict['text'][i]
                if lookfor.lower() == total_word:
                    if hasNumbers(lookfor):
                        total = re.sub("[^0-9][,.][^0-9]", "", lookfor)
                    elif hasNumbers(text_dict['text'][i + 1]):
                        total = re.sub("[^0-9][,.][^0-9]", "", text_dict['text'][i + 1])
                    else:
                        total = None
                    continue
                try:
                    total = re.findall(r"[-+]?\d*\.\d+|\d+", total)[0]
                except(TypeError):
                    total = float(0.00)
                try:
                    d = parse(lookfor, ignoretz=True)
                    if d is not None:
                        r = re.compile('.*-.*-.*')
                        reg = re.compile('.*/.*/.*')
                        if r.match(lookfor) or reg.match(lookfor):
                            datetime = d.strftime("%Y-%m-%d")
                        # datetime = datetime.date
                        #     print('matches')
                        # print("String: {} | Datetime: {}".format(lookfor, d))
                        # print("Type: {}".format(type(d)))
                        # if d is datetime.datetime:
                        #     datetime = d
                        # elif d is datetime.date:
                        #     date = d
                        # elif d is datetime.time:
                        #     time = d
                except(ValueError):
                    pass
                    # print(total_word + ": " + str(total))
                    # (x, y, w, h) = (text_dict['left'][i], text_dict['top'][i], text_dict['width'][i], text_dict['height'][i])
                    # (x1, y1, w1, h1) = (text_dict['left'][i + 1], text_dict['top'][i + 1], text_dict['width'][i + 1], text_dict['height'][i + 1])
                    # (x2, y2, w2, h2) = (text_dict['left'][i + 2], text_dict['top'][i + 2], text_dict['width'][i + 2], text_dict['height'][i + 2])
                    # cv2.rectangle(overlay, (x,y), (x1 + w1, y1 + h1), (0, 255, 0), -1)
                    # cv2.rectangle(overlay, (x2,y2), (x2 + w2, y2 + h2), (0, 0, 255), -1)
                    # alpha = 0.4  # Transparency factor.
                    # image_new = cv2.addWeighted(overlay, alpha, img, 1- alpha, 0)
                    # filename_new = 'result.jpg'
                    # image_new.save(os.path.join(app.config['UPLOAD_FOLDER'], filename_new))
            # cv2.imshow('img', image_new)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()
            # return render_template("image_text.html", text = text)
            return render_template("results.html", image = UPLOAD_FOLDER + filename, header = header, name = name, total = total, date_now = date.today().strftime("%Y-%m-%d"), datetime = datetime, category = category, language = language)

    else:
        return render_template("scan.html", categories = categories, languages = languages)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
