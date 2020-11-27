import mysql.connector
def init_mysql():
	db = mysql.connector.connect(
		host = "54.213.215.120",
		port = 51551,
		user = "admin",
		password = "ASJKOFFJOFJAOfjOFJAOFOKAFkOKGoKOKGOKoSK",
		database = "FORUM"
		)
	return db