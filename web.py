import sqlite3
from flask import Flask, request, render_template, flash, url_for, redirect
app = Flask(__name__)
app.secret_key = "Hello World"
db = sqlite3.connect("Login", check_same_thread = False)
cursor = db.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS LOGIN (USERNAME VARCHAR(10) UNIQUE, PASSWORD VARCHAR(10), ROOT BOOLEAN)")
db.set_trace_callback(print)

@app.route("/")
def index():
	return render_template("index.html")


@app.route("/register", methods = ["POST", "GET"])
def register():
	while True:
		if request.method == "POST":

			username = request.form["username"]
			password = request.form["password"]
			password_confirm = request.form["password_confirm"]
			if password == password_confirm:
				try:
					cursor.execute("INSERT INTO LOGIN VALUES (?, ?, False)", (username, password))
					db.commit()
				except sqlite3.IntegrityError:
					flash("Username has already been taken")
					return redirect(url_for("register"))
				return render_template("register_success.html")
			else:
				flash("Passwords didn't match")
				continue
		else:
			return render_template("register.html")


@app.route("/login", methods = ["POST", "GET"])
def login():
	if request.method == "POST":
		username = request.form["username"]
		password = request.form["password"]
		if username == "" or password == "":
			flash("Both fields are obligatory", "warning-error")
			return redirect(url_for("login"))

		db.set_trace_callback(print)
		cursor.execute("SELECT * FROM LOGIN WHERE USERNAME=(?) AND PASSWORD=(?)", (username, password))
		list = cursor.fetchall()
		print(list)
		if username in list[0] and password in list[0]:
			flash("Access Granted", "success")
		else:
			flash("Access Denied :(", "alert-error")
		return redirect(url_for("login"))
	else:
		return render_template("login.html")








if __name__ == '__main__':
	app.run(debug = True)
db.close()