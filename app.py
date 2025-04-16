import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, make_response

app = Flask(__name__, template_folder="templates")
CSV_FILE = "polls.csv"

# CSV column structure
COLUMNS = ["id", "poll"] + [f"option{i}" for i in range(1, 101)] + [f"votes{i}" for i in range(1, 101)]

def init_polls_csv():
    if not os.path.exists(CSV_FILE) or os.stat(CSV_FILE).st_size == 0:
        empty_df = pd.DataFrame(columns=COLUMNS)
        empty_df.to_csv(CSV_FILE, index=False)

def get_polls_df():
    df = pd.read_csv(CSV_FILE)
    if not df.empty:
        df.set_index("id", inplace=True)
    return df

init_polls_csv()

@app.route("/")
def index():
    polls_df = get_polls_df()
    return render_template("index.html", polls=polls_df)

@app.route("/polls/<id>")
@app.route("/polls/<id>")
@app.route("/polls/<id>")
def show_poll(id):
    polls_df = get_polls_df()
    id = int(id)
    if id not in polls_df.index:
        return "Poll not found", 404

    poll = polls_df.loc[id]

    # Gather all non-empty options dynamically
    options = [poll[f"option{i}"] for i in range(1, 101) if f"option{i}" in poll and not pd.isna(poll[f"option{i}"])]

    options_count = len(options)  # Count valid options

    return render_template("show_poll.html", poll=poll, poll_id=id, options=options, options_count=options_count)




@app.route("/vote/<id>/<option>")
def vote(id, option):
    id = int(id)
    option = str(option)
    cookie_key = f"vote_{id}_cookie"

    if request.cookies.get(cookie_key) is None:
        polls_df = get_polls_df()
        if id not in polls_df.index:
            return "Poll not found", 404

        column = "votes" + option
        if column not in polls_df.columns:
            return "Invalid vote option", 400

        polls_df.at[id, column] += 1
        polls_df.to_csv(CSV_FILE, index=True)

        response = make_response(redirect(url_for("show_poll", id=id, voted=True)))
        response.set_cookie(cookie_key, option)
        return response
    
    return f"You have already voted! Go back <a href='{url_for('show_poll', id=id)}'>here</a>"


@app.route("/polls", methods=["GET", "POST"])
@app.route("/polls", methods=["GET", "POST"])
def create_poll():
    if request.method == "GET":
        return render_template("new_poll.html")
    elif request.method == "POST":
        poll = request.form["poll"]

        # Dynamically fetch all options from the request
        options = [value for key, value in request.form.items() if key.startswith("option") and value.strip()]

        if not options:
            return "At least one option is required", 400

        polls_df = get_polls_df()
        new_id = max(polls_df.index.values) + 1 if not polls_df.empty else 1

        # Dynamically create a new poll dictionary
        new_poll = {**{"id": new_id, "poll": poll}, **{f"option{i+1}": opt for i, opt in enumerate(options)}, **{f"votes{i+1}": 0 for i in range(len(options))}}
        new_poll_df = pd.DataFrame([new_poll])
        new_poll_df.to_csv(CSV_FILE, mode='a', header=False, index=False)

        return redirect(url_for("index"))


@app.route("/delete/<id>")
def delete_poll(id):
    id = int(id)
    polls_df = get_polls_df()
    if id in polls_df.index:
        polls_df = polls_df.drop(id)
        polls_df.to_csv(CSV_FILE)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

