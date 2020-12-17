import string
import random
def generate_password():
	password_generate = ""
	for x in range(50):
		password_generate += random.choice(string.ascii_letters)
	return password_generate