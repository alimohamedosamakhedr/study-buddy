from flask import Flask, render_template, request, session, redirect
import csv
import random
import os
import webbrowser
import time 
app = Flask(__name__) 
app.secret_key = "quizkey"
 
csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Math.csv")

def Question():
    with open(csv_path, newline='', encoding='utf-8-sig') as f:
        questions = list(csv.DictReader(f))
    random.shuffle(questions)
    return questions[:5]

@app.route("/")
def index():
    #session for flask to store data
    session["questions"]= Question()
    session["current"]=1
    session["score"]=0
    session["start_time"] = time.time()
    return redirect("/quiz")

@app.route("/quiz")
def quiz():
    if "questions" not in session:
        return redirect("/")
    questions = session["questions"]
    current = session["current"]
    if current > len(questions):
        return redirect("/result")
    q = questions[current - 1 ]
    opts = {"A": q["a"], "B": q["b"], "C": q["c"], "D": q["d"]}
    return render_template("index.html", question=q["question"], opts=opts, num=current, total=len(questions))

@app.route("/answer", methods=["POST"])
def answer():
    questions = session["questions"]
    current = session["current"]
    ans = request.form.get("choice")
    correct = questions[current - 1]["ANSWER"].upper()
    if ans == correct:
        session["score"] += 1
    session["current"] += 1
    return redirect("/quiz")

@app.route("/result")
def result():
    end_time = time.time()                                
    time_taken = round(end_time - session["start_time"]) 
    return render_template("result.html", score=session["score"], total=len(session["questions"]),   time_taken=time_taken )

if __name__ == "__main__":
      app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5001)))
