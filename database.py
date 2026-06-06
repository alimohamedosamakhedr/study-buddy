import csv
from flask import Flask, render_template, request, session, redirect
import webbrowser
import hashlib #need to make the password hidden 
app = Flask(__name__) 
app.secret_key = "quizkey"

def get_next_id():
    with open("database.csv",  encoding='utf-8-sig') as f:
        rows= list(csv.DictReader(f))
        if rows:
            return int(rows[-1]["ID"])+1
        return 1
def register(username, password):   
    userid = get_next_id()
    with open("database.csv", "a", newline="", encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["ID", "USERNAME", "PASSWORD"])
        writer.writerow({"ID": userid, "USERNAME": username, "PASSWORD": password})
@app.route ("/register", methods=["GET","POST"])
def registerpage():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        register(username, password)       # ← still calls the register function
    return render_template("register.html")
if __name__ == "__main__":
    webbrowser.open("http://127.0.0.1:5000/register")
    app.run(debug=True)