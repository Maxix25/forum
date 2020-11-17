import sqlite3
from flask import Flask, request, render_template, flash, url_for, redirect, session
from datetime import timedelta, datetime
app = Flask(__name__)
app.secret_key = "Hello World"
app.permanent_session_lifetime = timedelta(days=180)
db = sqlite3.connect("login.sqlite3", check_same_thread = False)
cursor = db.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS LOGIN (USERNAME VARCHAR(10) UNIQUE, PASSWORD VARCHAR(10), ROOT BOOLEAN)")
cursor.execute("CREATE TABLE IF NOT EXISTS POSTS (ID INTEGER PRIMARY KEY AUTOINCREMENT, TITLE VARCHAR (20), CONTENT VARCHAR(200), AUTHOR VARCHAR(10), CREATED_AT DATETIME)")
db.set_trace_callback(print)

# Global Variables
authentication = False

# css-styling for flash messages
alert_error = "p-1 px-3 bg-red-600 text-white"
warning_error = "p-1 px-3 bg-yellow-400"
success = "p-1 px-3 bg-green-500 text-white"

@app.route("/")
def index():
	return render_template("index.html")


@app.route("/register", methods = ["POST", "GET"])
def register():
	try:
		if request.method == "POST":
			username = request.form["username"]
			if len(username) > 10:
				flash("The maximum length for the username is 10 characters", warning_error)
				return redirect(url_for("register"))
			password = request.form["password"]
			password_confirm = request.form["password_confirm"]
			if password == password_confirm:
				try:
					cursor.execute("INSERT INTO LOGIN VALUES (?, ?, 'False')", (username, password))
					db.commit()
				except sqlite3.IntegrityError:
					flash("Username has already been taken", alert_error)
					return redirect(url_for("register"))
				flash("Successfully registered!", success)
				return redirect(url_for("post"))
			else:
				flash("Passwords didn't match")
				return redirect(url_for("register"))
		else:
			return render_template("register.html")
	except Exception as e:
		print(e)


@app.route("/login", methods = ["POST", "GET"])
def login():
	try:
		if request.method == "POST":
			username = request.form["username"]
			password = request.form["password"]
			if username == "" or password == "":
				flash("Both fields are obligatory", warning_error)
				return redirect(url_for("login"))
			cursor.execute("SELECT * FROM LOGIN WHERE USERNAME=(?) AND PASSWORD=(?) LIMIT 1", (username, password))
			list = cursor.fetchall()
			if len(list) > 0:
				session["username"] = username
				session["password"] = password
				if request.form.get("rememberMe"):
					session.permanent = True
				flash("Access Granted", success)
				return redirect(url_for("post"))
			else:
				flash("Access Denied :(", alert_error)
				return redirect(url_for("login"))
		else:
			if "username" in session and "password" in session:
					return redirect(url_for("post"))
			return render_template("login.html")
	except Exception as e:
		print(e)


@app.route("/post", methods = ["POST", "GET"])
def post():
	cursor.execute("SELECT * FROM POSTS")
	posts = list(cursor.fetchall())[:5]
	print(posts)
	return render_template("posts.html", posts = posts)


# indivisual pages for posts
@app.route("/post/<int:post_id>")
def post_item(post_id):
	cursor.execute(f"SELECT * FROM POSTS WHERE ID = {post_id}")
	post = list(cursor.fetchone())
	id, title, content, author, created_at = post
	return render_template('post.html', title=title, content=content, author=author, created_at=created_at)


@app.route("/create", methods = ["POST", "GET"])
def create():
	if request.method == "POST":
		title = request.form["title"]
		content = request.form["content"]
		user = session['username']
		time = datetime.now()
		if title or content:
			cursor.execute("INSERT INTO POSTS VALUES (NULL, ?, ?, ?, ?)", (title, content, user, time))
			db.commit()
			flash("Your post has been submited!", success)
			return redirect(url_for("create"))
		else:
			flash("Please fill the mandatory fields properly", alert_error)
			return redirect(url_for("create"))
	else:
		if "username" in session and "password" in session:
			return render_template("create.html")
		else:
			return redirect(url_for("login"))
@app.route("/settings", methods = ["POST", "GET"])
def settings():
	global authentication
	if request.method == "POST":
		new_username = request.form["new_username"]
		new_password = request.form["new_password"]
		username = session["username"]
		password = session["password"]
		cursor.execute("SELECT * FROM LOGIN")
		cursor.execute("UPDATE LOGIN SET USERNAME=(?), PASSWORD=(?) WHERE USERNAME=(?) AND PASSWORD=(?)", (new_username, new_password, username, password))
		db.commit()
		session["username"] = new_username
		session["password"] = new_password
		flash("Credentials changed correctly!", success)
		return render_template("settings.html")
	else:
		if "username" in session and "password" in session:
			if authentication == True:
				authentication = False
				return render_template("settings.html")
			return redirect(url_for("authentication"))
		else:
			return redirect(url_for("login"))

@app.route("/authentication", methods = ["POST", "GET"])
def authentication():
	global authentication
	if request.method == "POST":
		username = request.form["username"]
		password = request.form["password"]
		cursor.execute("SELECT * FROM LOGIN WHERE USERNAME=(?) AND PASSWORD=(?)", (username, password))
		list = cursor.fetchall()
		if username in list[0] and password in list[0]:
			authentication = True
			return redirect(url_for("settings"))
		else:
			flash("Username or password are incorrect!", alert_error)
			return render_template("authentication.html")
	else:
		return render_template("authentication.html")


@app.route("/logout")
def logout():
	session.pop("username", None)
	session.pop("password", None)	
	flash("Successfully logged out!", success)
	return redirect(url_for("index"))


@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"), 404

if __name__ == '__main__':
	app.run(debug = True)
	db.close()