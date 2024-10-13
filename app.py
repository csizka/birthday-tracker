import os

import sqlite3
from flask import Flask, flash, jsonify, redirect, render_template, request

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Create SQL connection
db = sqlite3.connect(database = "birthdays.db", autocommit = True, check_same_thread = False)

MIN_MONTH = 1
MAX_MONTH = 12
DAYS = [31,29,31,30,31,30,31,31,30,31,30,31]

def render_index(submission_message):
    birthdays_result = db.execute("SELECT * FROM birthdays ORDER BY month, day;")
    col_names = [ col_desc[0] for col_desc in list(birthdays_result.description) ]
    bday_records = birthdays_result.fetchall()
    birthdays = [ dict(zip(col_names, bday_rec)) for bday_rec in bday_records ]
    return render_template("index.html", birthdays=birthdays, submission_message=submission_message)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":

        name = request.form.get("name")
        if not name:
            submission_message = "Birthday not submitted due to lack of name."
            return render_index(submission_message)

        month = request.form.get("month")
        if not month:
            submission_message = "Birthday not submitted due to lack of month."
            return render_index(submission_message)

        try:
            month = int(month)
        except ValueError:
            submission_message = "Birthday not submitted due to ivalid month format."
            return render_index(submission_message)

        if month < MIN_MONTH or month > MAX_MONTH:
            submission_message = "Birthday not submitted due to ivalid month format."
            return render_index(submission_message)

        day = request.form.get("day")
        if not day:
            submission_message = "Birthday not submitted due to lack of day."
            return render_index(submission_message)

        try:
            day = int(day)
        except ValueError:
            submission_message = "Birthday not submitted due to invalid day format."
            return render_index(submission_message)

        if day > DAYS[month - 1] or day < 1:
            submission_message = "Birthday not submitted due to invalid day format."
            return render_index(submission_message)

        db.execute("INSERT INTO birthdays (name, month, day) VALUES(?, ?, ?)", (name, month, day))
        submission_message = "Birthday successfully submitted."
        return render_index(submission_message)

    else:
        return render_index("")

@app.route("/delete", methods=["POST"])
def delete_bday():
    id = request.form.get("id")
    if id:
        db.execute("DELETE FROM birthdays WHERE id = ?", id)
    submission_message = "Deletion successful."
    return render_index(submission_message)



