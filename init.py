import os
import mysql.connector
from authlib.integrations.flask_client import OAuth
from flask_dance.contrib.github import make_github_blueprint, github
def init_mysql():
	db = mysql.connector.connect(
		host = os.environ.get("DB_HOST"),
		port = 3306,
		user = os.environ.get("DB_USER"),
		password = os.environ.get("DB_PASSWORD"),
		database = os.environ.get("DB_NAME")
		)
	return db
def init_google(oauth):
	google = oauth.register(
	name='google',
	client_id = os.environ.get("GOOGLE_CLIENT_ID"),
	client_secret = os.environ.get("GOOGLE_CLIENT_SECRET"),
	access_token_url = 'https://accounts.google.com/o/oauth2/token',
	access_token_params = None,
	authorize_url = 'https://accounts.google.com/o/oauth2/auth',
	authorize_params = None,
	api_base_url = 'https://www.googleapis.com/oauth2/v1/',
	userinfo_endpoint = 'https://openidconnect.googleapis.com/v1/userinfo',  # This is only needed if using openId to fetch user info
	client_kwargs = {'scope': 'openid email profile'},
	)
	return google
def init_github():
	github_blueprint = make_github_blueprint(client_id = os.environ.get("GITHUB_CLIENT_ID"), client_secret = os.environ.get("GITHUB_CLIENT_SECRET"))
	return github_blueprint