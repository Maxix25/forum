import os
from flask import Flask, request, render_template, flash, url_for, redirect, session
from datetime import timedelta, datetime
from generate_password import generate_password
from init import init_mysql, init_google, init_github
from authlib.integrations.flask_client import OAuth
app = Flask(__name__)
app.secret_key = generate_password()
app.permanent_session_lifetime = timedelta(days=180)

db = init_mysql()


# OAuth apps
oauth = OAuth(app)
google = init_google(oauth)

github_blueprint = init_github()
app.register_blueprint(github_blueprint, url_prefix = "/github_login")


cursor = db.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS USERS (USERNAME VARCHAR(10) UNIQUE NOT NULL, PASSWORD VARCHAR(10) NOT NULL, DESCRIPTION VARCHAR(100) NOT NULL)")
cursor.execute("CREATE TABLE IF NOT EXISTS POSTS (POSTID INTEGER PRIMARY KEY AUTO_INCREMENT, TITLE VARCHAR (20), CONTENT VARCHAR(200), AUTHOR VARCHAR(10), CREATED_AT DATETIME)")
db.commit()

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
			print(username)
			password = request.form["password"]
			print(password)
			password_confirm = request.form["password_confirm"]
			description = request.form["description"]
			if len(username) == 0 or len(password) == 0 or len(description) == 0:
				flash("All fields are obligatory", alert_error)
				return redirect(url_for("register"))
			if password == password_confirm:
				try:
					cursor.execute(f"INSERT INTO USERS (USERNAME, PASSWORD, DESCRIPTION) VALUES (%s, %s, %s)", (username, password, description))
					db.comm>it()
					flash("Successfully registered!", success)
					return redirect(url_for("post"))
				except mysql.connector.IntegrityError:
					flash("Username already taken", warning_error)
					return render_template("register.html")
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
			cursor.execute(f"SELECT USERNAME, PASSWORD FROM USERS WHERE USERNAME=(%s) AND PASSWORD=(%s) LIMIT 1", (username, password))
			print(cursor.statement)
			list = cursor.fetchall()
			print(list)
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

@app.route("/login/google")
def login_google():
	google = oauth.create_client('google')
	redirect_uri = url_for('authorize', _external=True)
	return oauth.google.authorize_redirect(redirect_uri)

@app.route("/authorize")
def authorize():
	google = oauth.create_client('google')
	token = oauth.google.authorize_access_token()
	resp = google.get('userinfo')
	user_info = resp.json()
	print(user_info)
	# do something with the token and profile
	session["picture"] = user_info["picture"]
	session["username"] = user_info["name"]
	session["password"] = True
	return redirect('/post')

@app.route('/github_login')
def github_login():
	if not github.authorized:
		return redirect(url_for('github.login'))
	else:
		account_info = github.get('/user')
		if account_info.ok:
			account_info_json = account_info.json()
			return '<h1>Your Github name is {}'.format(account_info_json['login'])

	return '<h1>Request failed!</h1>'

@app.route("/post", methods = ["POST", "GET"])
def post():
	if request.method == "POST":
		search = request.form["search"]
		cursor.execute(f"SELECT * FROM POSTS WHERE TITLE LIKE '{search}%' OR CONTENT LIKE '{search}%' ORDER BY CREATED_AT")
		search_results = cursor.fetchall()
		print(search_results)
		return render_template("posts.html", search_results = search_results, counter = 0)
	else:
		cursor.execute("SELECT * FROM POSTS")
		posts = list(cursor.fetchall())[:5]
		print(posts)
		return render_template("posts.html", posts = posts)


# indivisual pages for posts
@app.route("/post/<int:post_id>")
def post_item(post_id):
	cursor.execute(f"SELECT * FROM POSTS WHERE POSTID = {post_id}")
	post = list(cursor.fetchone())
	id, title, content, author, created_at = post
	return render_template('post.html', title=title, content=content, author=author, created_at=created_at)


@app.route("/create", methods = ["POST", "GET"])
def create():
	if request.method == "POST":
		title = request.form["title"]
		content = request.form["content"]
		author = session['username']
		time = datetime.now()
		if title != "" and content != "":
			cursor.execute(f"INSERT INTO POSTS (POSTID, TITLE, CONTENT, AUTHOR, CREATED_AT) VALUES (NULL, %s, %s, %s, %s)", (title, content, author, time))
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
		try:
			cursor.execute(f"UPDATE USERS SET USERNAME=%s, PASSWORD=%s WHERE USERNAME=%s", (new_username, new_password, username))
			db.commit()
		except mysql.connector.IntegrityError:
			flash("Username already taken", warning_error)
			return render_template("settings.html")
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

@app.route("/<username>", methods = ["POST", "GET"])
def user_page(username):
	image = session["picture"]
	print(image)
	try:
		if request.method == "POST":
			return render_template("user_page.html")
		else:
			cursor.execute(f"SELECT USERNAME, DESCRIPTION FROM USERS WHERE USERNAME='{username}'")
			list = cursor.fetchall()
			username = list[0][0]
			description = list[0][1]
			return render_template("user_page.html", username = username, description = description, image = image)
	except IndexError:
		print("Hello World")
		return render_template("404.html")

@app.route("/authentication", methods = ["POST", "GET"])
def authentication():
	global authentication
	if request.method == "POST":
		password = request.form["password"]
		if "username" in session and "password" in session["password"]:
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
