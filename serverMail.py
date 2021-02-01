import smtplib
import os
import datetime
import socket
from sqlite3 import *
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import email
import mimetypes
import imaplib
from email.header import decode_header
import webbrowser
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import base64,os, json


#You have to install with pip : 
#pip install cryptography



#1) Connect your mail server (Google ...) 
#For the information, you will need to enter your host and port, here there is the port dependably on your account https://assistance.orange.fr/mobile-tablette/tous-les-mobiles-et-tablettes/installer-et-utiliser/utiliser-internet-mail-et-cloud/mail/l-application-mail-orange/parametrer-et-configurer/comment-configurer-les-serveurs-sortants-et-entrants-des-principaux-comptes-mails-_47992-48856
#For example, for orange : host = smtp.orange.fr, port = 465/for gmail : host = smtp.gmail.com, port = 465
def connectServer(): #Here, the function connectServer that we will use several times for each question.
	case = input("Have you already your account registered ? \n0 = Yes / 1 = No (to register and connect to it)\n") #We simply ask if the user has an account or not
	if (case=="0"): #If it has, we will retrieve his information from the database.
		username = input("Enter your mail : ") #For that, he enters his mail
		conn = connect("maildatabase.db") #We connect to the database
		cur = conn.cursor() #We will use a cursor to execute an sql reques
		try:
			cur.execute("SELECT password, smtp_host, smtp_port FROM account where mail=?", (username,)) #We request his information of his account
			r = cur.fetchone() #We retrieve them
			password = r[0] #We attribute each information (password, host, port)
			smtp_ssl_host = r[1]
			smtp_ssl_port = r[2]
			ok = True
			try:
				server = smtplib.SMTP_SSL(smtp_ssl_host, smtp_ssl_port) #We connect to the server by using an host and port securised
				print("The service is securised.") 
				server.login(username, password) #We login 
				print("You are now connecting to your email server : "+str(smtp_ssl_host)) 
				keepLogs("Connection to the server realized.") #We keep the logs of the connection 
			except Exception:
				print("One of the field is not correct.") #If it didn't work, we display an error message and we keep the logs of the fail.
				keepLogs("Failed to connect to the server.")
			cur.close() #We close the cursor
			conn.close() #We close the connection
		except Error: #If it didn't succeed to connect, we print an error.
			ok = False
			cur.close()
			conn.close()
			print("You are not registered or is not that mail.")
	elif (case=="1"): #In the case 1, he has to insert his account into the database
		smtp_ssl_host = input("Can you enter the smtp_ssl_host of your email server (example for gmail smtp.gmail.com) : ") #he enters the host of his account 
		smtp_ssl_port = input("Can you enter the smtp_ssl_port of your email server (choose 465 by default) : ") #then, the port of this host
		username = input("Enter your email : ") #His email 
		password = input("Enter your password : ") #His password
		#Check the validity of the format of the 4 entries.
		try:
			server = smtplib.SMTP_SSL(smtp_ssl_host, smtp_ssl_port) #we connect to the server by using a host and port securised
			print("The service is securised.")
			server.login(username, password) #We login
			print("You are now connecting to your email server : "+str(smtp_ssl_host))
			conn = connect("maildatabase.db") #We connect to the database
			cur = conn.cursor() 
			try:
				cur.execute("INSERT INTO account(mail, password, smtp_host, smtp_port) VALUES(?,?,?,?)", (username, password, smtp_ssl_host, smtp_ssl_port)) #We execute the request to insert the account into the db
				conn.commit()
				print("Your account is registered into the database.")
				cur.close() #We commit and close the cursor and connection.
				conn.close()
				keepLogs("Connection to the server and adding the account to the database realized.") #We keep the logs that an account has been added.
			except Error: 
				print("An error has occured in registering your account into the database.") #If it fails to register, we keep the logs
				keepLogs("Failed to connect to the server.")
		except Exception: #We print an error if he can't connect to the server
			print("One of the field is not correct.")

#2) To add another account to your database (here, we just want to add it, not to connect to)
def addAccount(): 
		smtp_ssl_host = input("Can you enter the smtp_ssl_host of your email server (example for gmail smtp.gmail.com) : ") #We take the host 
		smtp_ssl_port = input("Can you enter the smtp_ssl_port of your email server (choose 465 by default) : ") #We take the port 
		username = input("Enter your email : ") #We take the username
		password = input("Enter your password : ") #We take the password
		conn = connect("maildatabase.db") #And then we connect to the db 
		cur = conn.cursor()	#We use a cursor to execute a request
		try:
			cur.execute("INSERT INTO account(mail, password, smtp_host, smtp_port) VALUES(?,?,?,?)", (username, password, smtp_ssl_host, smtp_ssl_port))
			conn.commit() #Then, we execute the request and insert the information into the db and commit it before closing the connection and cursor.
			print("Your account is registered into the database.")
			cur.close()
			conn.close()
			keepLogs("Account added to the database.") #We keep the logs that an account has been added.
		except Error:
			keepLogs("Attempt to add account to the database failed.") #We keep the logs that it has failed and print it.
			print("The account is already present or one of the field is incorrect.")

#3) To retrieve emails from the database SQLite 
def retrieveEmails(): 
	username = input("Enter your mail : ") #We asks the mail
	conn = connect("maildatabase.db") #We connect to the dbd
	cur = conn.cursor() #We create a cursor
	try:
		cur.execute("SELECT * FROM emails where account=?", (username,))
		r = cur.fetchall() #We execute the request and get all the emails from the account 
		print("Your email(s) : ")
		for i in r:
			print(str(i[0])+" | From : "+str(i[2])+", To : "+str(i[3])+"\nSubject : "+str(i[4])+"\nMessage : "+str(i[5]))
		cur.close() #We print each emails, and then close the connection and the cursor.
		conn.close()
		keepLogs("Retrieved emails from the database.") #We keep the logs that it has retrieved emails
	except Error:
		ok = False
		cur.close()
		conn.close()
		keepLogs("Attempt to retrieve emails failed.")
		print("You are not registered or is not that mail.") #If it has failed to connect to the db, we close the cursor, connection and keep the logs, and print an error.

#4) Ability to read emails
#QUESTION 4 = READ EMAILS WITH ATTACHMENTS, so it's the same that the bonus #1.


#5) Possibility to send emails
def sendMail():
	case = input("Have you already your account registered ? \n0 = Yes / 1 = No (to register and connect to it)\n")
	if (case=="0"):
		username = input("Enter your mail : ")
		conn = connect("maildatabase.db")
		cur = conn.cursor()
		try:
			cur.execute("SELECT password, smtp_host, smtp_port FROM account where mail=?", (username,))
			r = cur.fetchone()
			password = r[0]
			smtp_ssl_host = r[1]
			smtp_ssl_port = r[2]
			ok = True
			try:
				server = smtplib.SMTP_SSL(smtp_ssl_host, smtp_ssl_port)
				print("The service is securised.")
				server.login(username, password)
				print("You are now connecting to your email server : "+str(smtp_ssl_host))
				keepLogs("Connection to the server realized.")
			except Exception:
				print("One of the field is not correct.")
				keepLogs("Failed to connect to the server.")
			cur.close()
			conn.close()
		except Error:
			ok = False
			cur.close()
			conn.close()
			print("You are not registered or is not that mail.")
	elif (case=="1"):
		smtp_ssl_host = input("Can you enter the smtp_ssl_host of your email server (example for gmail smtp.gmail.com) : ")
		smtp_ssl_port = input("Can you enter the smtp_ssl_port of your email server (choose 465 by default) : ")
		username = input("Enter your email : ")
		password = input("Enter your password : ")
		#Check the validity of the format of the 4 entries.
		try:
			server = smtplib.SMTP_SSL(smtp_ssl_host, smtp_ssl_port)
			print("The service is securised.")
			server.login(username, password)
			print("You are now connecting to your email server : "+str(smtp_ssl_host))
			conn = connect("maildatabase.db")
			cur = conn.cursor()
			try:
				cur.execute("INSERT INTO account(mail, password, smtp_host, smtp_port) VALUES(?,?,?,?)", (username, password, smtp_ssl_host, smtp_ssl_port))
				conn.commit()
				print("Your account is registered into the database.")
				cur.close()
				conn.close()
				keepLogs("Connection to the server and adding the account to the database realized.")
			except Error:
				print("An error has occured in registering your account into the database.")
				keepLogs("Failed to connect to the server.")
		except Exception:
			print("One of the field is not correct.")
	targets = [] #We create an empty list of targets
	while True: #While the user want to add a target, he can
		target = input("Enter the target(s) of your email (if it's finished, write Stop) : ")
		targets.append(target)
		if targets[len(targets)-1] == "Stop": #When he writes Stop, that stop the while.
			targets.remove('Stop')
			break
	subject = input("Enter the subject of your email : ") #We ask the subject of the email
	message = input("Enter the message of your email : ") #We ask the message of the email 
	msg = MIMEText(message) #We create a mime (it is used for the emails)
	msg['Subject'] = subject #We put the subject = to the subject asked
	msg['From'] = username #We put the sender = to the mail used 
	msg['To'] = ', '.join(targets) #We put all the targets = to the targets asked
	server.sendmail(username, targets, msg.as_string()) #We send the mail with the function sendmail(mail, msg)
	server.quit() #We quit the server
	keepLogs("An email was sent.") #We keep the logs that an email was sent and print that.
	print("You just sent your email to : "+str(targets))	

#6) Sorting the emails by (De, To, Subject)
def sortEmails():
	username = input("Enter your mail : ") #We ask the mail to be used
	conn = connect("maildatabase.db") #We connect to the database
	cur = conn.cursor() #We create a cursor
	try: #Then, we will sort by using a request SQL, we will sort wheter by Sender, Receiver, Subject or ID.
		sortBy = input("Sort your emails : Sender / Receiver / Subject / ID\nBy : ")
		if (sortBy == "Sender"):
			cur.execute("SELECT * from emails WHERE account=? ORDER BY sender", (username,))
			mailSorted = cur.fetchall() #We get the emails and print them in the sorted order and so on for each if (sort...)
			print("Your email(s) sorted by sender: ")
			for i in mailSorted:
				print(str(i[0])+" | From : "+str(i[2])+", To : "+str(i[3])+"\nSubject : "+str(i[4])+"\nMessage : "+str(i[5]))
			conn.commit() #Commit your changes in the database
		elif (sortBy == "Receiver"):
			cur.execute("SELECT * from emails WHERE account=? ORDER BY receiver", (username,))
			mailSorted = cur.fetchall()
			print("Your email(s) sorted by receiver: ")
			for i in mailSorted:
				print(str(i[0])+" | From : "+str(i[2])+", To : "+str(i[3])+"\nSubject : "+str(i[4])+"\nMessage : "+str(i[5]))
			conn.commit() #Commit your changes in the database
		elif (sortBy == "Subject"):
			cur.execute("SELECT * from emails WHERE account=? ORDER BY subject", (username,))
			mailSorted = cur.fetchall()
			print("Your email(s) sorted by subject: ")
			for i in mailSorted:
				print(str(i[0])+" | From : "+str(i[2])+", To : "+str(i[3])+"\nSubject : "+str(i[4])+"\nMessage : "+str(i[5]))
			conn.commit() #Commit your changes in the database
		elif (sortBy == "ID"):
			cur.execute("SELECT * from emails WHERE account=? ORDER BY subject", (username,))
			mailSorted = cur.fetchall()
			print("Your email(s) sorted by ID: ")
			for i in mailSorted:
				print(str(i[0])+" | From : "+str(i[2])+", To : "+str(i[3])+"\nSubject : "+str(i[4])+"\nMessage : "+str(i[5]))
			conn.commit() #Commit your changes in the database
		ok = True
		cur.close()
		conn.close()
		keepLogs("Sorted emails.") #We close the connection, the cursor and keep the logs that the emails has been sorted.
	except Error:
		ok = False 
		cur.close()
		conn.close()
		keepLogs("Failed to sort emails.") #We keep the logs that something has failed and print the error.
		print("You are not registered or is not that mail.")


#7) Log of connections to the mail server (login, @IP, date, etc.) 
def keepLogs(requete): #We put requete in attribute to name the requete dependably on the function used.
	conn = connect("maildatabase.db") #We connect to the database, create a cursor
	cur = conn.cursor()	
	dateNow = datetime.datetime.now() #We get the information of the date, the hostname (=the name of the computer used) and the IP used.
	hostname = socket.gethostname()
	ip_address = socket.gethostbyname(hostname)
	try:
		cur.execute("INSERT INTO logs(dateLog, ip, hostname, requete) VALUES(?,?,?,?)", (dateNow, hostname, ip_address, requete)) 
		conn.commit() #We insert the logs into the database and commit it.
		print("The logs have been registered.")
		cur.close()
		conn.close() #We close the cursor, the connection and print that the logs have been registered.
	except Error:
		print("An error has occured in the logs.") #We print an error if it has failed.

def displayLogs(): #To display the logs
	conn = connect("maildatabase.db") #We connect to the db and create a cursor
	cur = conn.cursor()	
	try:
		cur.execute("SELECT * from logs") #We select all the logs and print them.
		print("The logs : \n")
		for row in cur.fetchall():
			print(row)
		cur.close()
		conn.close()
		keepLogs("Displayed the logs.") #We keep a logs that someone has displayed the logs.
	except Error:
		print("An error has occured in the logs.") #We print an error if it has failed and keep the logs that has failed.
		keepLogs("Failed to display the logs.")

#8) Saving emails to a file 
def savingsEmails():
	username = input("Enter your mail : ") #We ask the mail 
	conn = connect("maildatabase.db") #We connect to the db and create a cursor
	cur = conn.cursor()
	choice = input("Do you want to save one mail or all your emails ?\n1 = One | 2 = All\nNumber = ")
	if (choice=="1"):
		try:
			cur.execute("SELECT * FROM emails where account=?", (username,)) #We select all the mails from the account
			r = cur.fetchall()
			print("Your email(s) : ") #We print all the emails from the account
			for i in r:
				print(str(i[0])+" | From : "+str(i[2])+", To : "+str(i[3])+"\nSubject : "+str(i[4])+"\nMessage : "+str(i[5]))
			numID = input("Enter the ID (numero of identification) of the mail that you want to save : ") #We ask the user to choose which emails he want to save
			cur.execute("SELECT * from emails where id=?", (numID)) #We get the email that he wants to keep
			emailSaved = cur.fetchone()
			pathtofile = input("Enter the path where you want to save that file and with the name of the file\nExample on Windows C:\\Users\\samy\\Desktop\\nameFile.txt \nThe path : ") #We ask the user where he wants to save the file
			f = open(pathtofile, "w") #We open a new file (it is where we will save the file)
			f.write(str(emailSaved[0])+" | From : "+str(emailSaved[2])+", To : "+str(emailSaved[3])+"\nSubject : "+str(emailSaved[4])+"\nMessage : "+str(emailSaved[5]))
			f.close() #We write the file with the information of the email and close it.
			print("The file has been registered into your directory selected.")
			cur.close()
			conn.close() #We close the connection, cursor, and keep the logs that an email has been saved.
			keepLogs("Saved an email to a file.")
		except Error:
			ok = False
			cur.close()
			conn.close() #We close the cursor, connection, and keep the logs that something has failed and print the error.
			print("You are not registered or is not that mail.")
			keepLogs("Failed to save an email.")
	elif (choice=="2"):
		try:
			cur.execute("SELECT * FROM emails where account=?", (username,)) #We select all the mails from the account
			r = cur.fetchall()
			pathtofile = input("Enter the path where you want to save that file and with the name of the file\nExample on Windows C:\\Users\\samy\\Desktop\\nameFile.txt \nThe path : ") #We ask the user where he wants to save the file
			f = open(pathtofile, "w") #We open a new file (it is where we will save the file)
			for i in r:
				f.write(str(i[0])+" | From : "+str(i[2])+", To : "+str(i[3])+"\nSubject : "+str(i[4])+"\nMessage : "+str(i[5]))
			f.close() #We write the file with the information of the email and close it.
			print("The file has been registered into your directory selected.")
			cur.close()
			conn.close() #We close the connection, cursor, and keep the logs that an email has been saved.
			keepLogs("Saved the emails to a file.")
		except Error2:
			ok = False
			cur.close()
			conn.close() #We close the cursor, connection, and keep the logs that something has failed and print the error.
			print("You are not registered or is not that mail.")
			keepLogs("Failed to save the emails.")			

#9) Your original feature
def originalFeature():
	conn = connect("maildatabase.db") #We connect to the db and create a cursor
	cur = conn.cursor()
	choice = input("What do you want to do ?\n1 = Update your password from one of your account\n2 = Remove one of your account\n3 = Remove one of your emails\n Choice = ") #We suggest some choices
	username = input("Enter your mail : ") #We ask the mail of the user
	if (choice == "1"): #If choice ==1, we will update the password
		nameAccount = input("Enter the account which you want modify the password : ")
		password = input("Enter the new password : ") #For that, we ask the mail and the new password
		try:
			cur.execute("UPDATE account SET password=? where mail=?", (password, nameAccount))
			conn.commit() #We update the password, and commit it, and keep the logs that it has modified his password.
			print("Your password has been modified.")
			keepLogs("A password has been modified.")
		except Error:
			print("Failed to update the password.") #If an error is prompted, we keep the logs that it has failed and print the error.
			keepLogs("Failed to update the password.")
		cur.close() #We close the cursor and connection
		conn.close()
	elif (choice == "2"):
		cur.execute("SELECT * FROM account") #We select all the accounts to print them
		r = cur.fetchall()
		print("Your mail(s) : ") #We print all the account
		for i in r:
			print(str(i[0])+" | Password = "+str(i[1])+"\nHOST = "+str(i[2])+" & PORT = "+str(i[3]))
		nameMail = input("Enter the mail (account) that you want to delete : ") #We ask the account that will be deleted.
		try:
			cur.execute("DELETE FROM account where mail=?", (nameMail,))
			conn.commit()
			print("The account has been deleted.")
			keepLogs("An account has been deleted.")
		except Error:
			print("Failed to deleted the account.")
			keepLogs("Failed to delete the account.")
		cur.close()
		conn.close()
	elif (choice == "3"):
		cur.execute("SELECT * FROM emails where account=?", (username,)) #We select all the emails from the account
		r = cur.fetchall()
		print("Your email(s) : ") #We print all the emails
		for i in r:
			print(str(i[0])+" | From : "+str(i[2])+", To : "+str(i[3])+"\nSubject : "+str(i[4])+"\nMessage : "+str(i[5]))
		numID = input("Enter the ID (numero of identification) of the mail that you want to delete : ") #We ask the id of which email to delete
		try:
			cur.execute("DELETE FROM emails where id=?", (numID)) #We delete the email
			conn.commit() #We commit it, print it and keep the logs
			print("The email has been deleted.")
			keepLogs("An email has been deleted.")	
		except Error:
			print("Failed to delete the email.") #We print an error if one has occured and keep the logs.
			keepLogs("Failed to delete the email.")
		cur.close()
		conn.close() #We close the connection the cursor.

#######
#BONUS#
#######
#1) Ability to read and send emails with attachments
def q10():
	number = input("Do you want to send an attachment, or read an email (and its attachment(s)) ?\n1 = Send | 2 = Read\nNumber = ")
	if (number == "1"):
		sendAttach()
	elif (number == "2"):
		readMailsAndAttachment()

#To send an email with attachments
def sendAttach():
	case = input("Have you already your account registered ? \n0 = Yes / 1 = No (to register and connect to it)\n")
	if (case=="0"):
		username = input("Enter your mail : ")
		conn = connect("maildatabase.db")
		cur = conn.cursor()
		try:
			cur.execute("SELECT password, smtp_host, smtp_port FROM account where mail=?", (username,))
			r = cur.fetchone()
			password = r[0]
			smtp_ssl_host = r[1]
			smtp_ssl_port = r[2]
			ok = True
			try:
				server = smtplib.SMTP_SSL(smtp_ssl_host, smtp_ssl_port)
				print("The service is securised.")
				server.login(username, password)
				print("You are now connecting to your email server : "+str(smtp_ssl_host))
				keepLogs("Connection to the server.")
			except Exception:
				print("One of the field is not correct.")
				keepLogs("Failed to connect to the server.")
			cur.close()
			conn.close()
		except Error:
			ok = False
			cur.close()
			conn.close()
			print("You are not registered or is not that mail.")
	elif (case=="1"):
		smtp_ssl_host = input("Can you enter the smtp_ssl_host of your email server (example for gmail smtp.gmail.com) : ")
		smtp_ssl_port = input("Can you enter the smtp_ssl_port of your email server (choose 465 by default) : ")
		username = input("Enter your email : ")
		password = input("Enter your password : ")
		#Check the validity of the format of the 4 entries.
		try:
			server = smtplib.SMTP_SSL(smtp_ssl_host, smtp_ssl_port)
			print("The service is securised.")
			server.login(username, password)
			print("You are now connecting to your email server : "+str(smtp_ssl_host))
			conn = connect("maildatabase.db")
			cur = conn.cursor()
			try:
				cur.execute("INSERT INTO account(mail, password, smtp_host, smtp_port) VALUES(?,?,?,?)", (username, password, smtp_ssl_host, smtp_ssl_port))
				conn.commit()
				print("Your account is registered into the database.")
				keepLogs("Connection to the server and adding the account to the database realized.")
				cur.close()
				conn.close()
			except Error:
				print("An error has occured in registering your account into the database.")
				keepLogs("Failed to connect to the server.")
		except Exception:
			print("One of the field is not correct.")
	targets = []
	while True:
		target = input("Enter the target(s) of your email (if it's finished, write Stop) : ")
		targets.append(target)
		if targets[len(targets)-1] == "Stop":
			targets.remove('Stop')
			break
	subject = input("Enter the subject of your email : ")
	message = input("Enter the message of your email : ")
	msg = MIMEMultipart()
	msg['Subject'] = subject
	msg['From'] = username
	msg['To'] = ', '.join(targets)
	txt = MIMEText(message)
	msg.attach(txt)
	paths = []
	while True: #While true, we ask a new file to add (here only the image files work)
		print("Example of path : C:\\Users\\samy\\Desktop\\img.png")
		pathtofile = input("Enter the path to your file (if it's finished, write Stop) : ") #We ask the path to the file (on your computer)
		paths.append(pathtofile) #We append it to the list
		if paths[len(paths)-1] == "Stop": #If the user mark Stop, we stop.
			paths.remove("Stop")
			break
		filepath = pathtofile 
		with open(filepath, 'rb') as f: #We open each file, and attach it to the emails that will be send.
			img = MIMEImage(f.read())
			img.add_header('Content-Disposition','attachment',filename=os.path.basename(filepath))
		msg.attach(img)
	#CONNECT VIA FUNCTION OR DIRECTLY ?
	server.sendmail(username, targets, msg.as_string())
	server.quit()
	print("You just sent your email with attachments to : "+str(targets))
	keepLogs("An email with an attachment was sent.")

#TO READ EMAILS : https://www.thepythoncode.com/article/reading-emails-in-python

def clean(text):
    # clean text for creating a folder
    return "".join(c if c.isalnum() else "_" for c in text)

def readMailsAndAttachment():
	case = input("Have you already your account registered ? \n0 = Yes / 1 = No (to register and connect to it)\n")
	if (case=="0"):
		username = input("Enter your mail : ")
		host_protocol = input("Enter the host of the protocol (IMAP/POP3, example : imap.orange.fr) : ")
		conn = connect("maildatabase.db")
		cur = conn.cursor()
		try:
			cur.execute("SELECT password, smtp_host, smtp_port FROM account where mail=?", (username,))
			r = cur.fetchone()
			password = r[0]
			ok = True
			try:
				server = imaplib.IMAP4_SSL(host_protocol)
				print("The service is securised.")
				server.login(username, password)
				print("You are now connecting to your email server : "+str(host_protocol))
				keepLogs("Connection to the server realized.")
			except Exception:
				print("One of the field is not correct.")
				keepLogs("Failed to connect to the server.")
			cur.close()
			conn.close()
		except Error:
			ok = False
			cur.close()
			conn.close()
			print("You are not registered or is not that mail.")
	elif (case=="1"):
		smtp_ssl_host = input("Can you enter the smtp_ssl_host of your email server (example for gmail smtp.gmail.com) : ")
		smtp_ssl_port = input("Can you enter the smtp_ssl_port of your email server (choose by default 465) : ")
		username = input("Enter your email : ")
		password = input("Enter your password : ")
		#Check the validity of the format of the 4 entries.
		try:
			server = imaplib.IMAP4_SSL(host_protocol)
			print("The service is securised.")
			server.login(username, password)
			print("You are now connecting to your email server : "+str(host_protocol))
			conn = connect("maildatabase.db")
			cur = conn.cursor()
			try:
				cur.execute("INSERT INTO account(mail, password, smtp_host, smtp_port) VALUES(?,?,?,?)", (username, password, smtp_ssl_host, smtp_ssl_port))
				conn.commit()
				print("Your account is registered into the database.")
				cur.close()
				conn.close()
				keepLogs("Connection to the server and adding the account to the database realized.")
			except Error:
				print("An error has occured in registering your account into the database.")
				keepLogs("Failed to connect to the server.")
		except Exception:
			print("One of the field is not correct.")
	status, messages = server.select("INBOX")
	N = int(input("Enter the number of your last emails that you want to see : ")) #Number of top emails to fetch
	messages = int(messages[0]) #Total number of emails
	for i in range(messages, messages-N, -1):
	    res, msg = server.fetch(str(i), "(RFC822)") #Fetch the email message by ID
	    for response in msg:
	        if isinstance(response, tuple):
	            msg = email.message_from_bytes(response[1]) #Parse a bytes email into a message object
	            subject, encoding = decode_header(msg["Subject"])[0] #Decode the email subject
	            if isinstance(subject, bytes):
	                subject = subject.decode(encoding) #If it's a bytes, decode to str
	            From, encoding = decode_header(msg.get("From"))[0] #Decode email sender
	            if isinstance(From, bytes):
	                From = From.decode(encoding)
	            print("Subject : ", subject)
	            print("From : ", From) 
	            if msg.is_multipart(): #If the email message is multipart
	                for part in msg.walk():  #Iterate over email parts
	                    content_type = part.get_content_type() #Extract content type of email
	                    content_disposition = str(part.get("Content-Disposition"))
	                    try:
	                        body = part.get_payload(decode=True).decode() #Get the email body
	                    except:
	                        pass
	                    if content_type == "text/plain" and "attachment" not in content_disposition: #Print text/plain emails and skip attachments
	                        print(body)
	                    elif "attachment" in content_disposition: #Download attachment
	                        filename = part.get_filename()
	                        if filename:
	                            folder_name = clean(subject)
	                            if not os.path.isdir(folder_name): #Make a folder for this email (named after the subject) 
	                                os.mkdir(folder_name)
	                            filepath = os.path.join(folder_name, filename) #Download attachment and save it
	                            open(filepath, "wb").write(part.get_payload(decode=True))
	            else: 
	                content_type = msg.get_content_type() #Extract content type of email
	                body = msg.get_payload(decode=True).decode() #Get the email body
	                if content_type == "text/plain": #Print only text email parts
	                    print(body)
	            if content_type == "text/html": #If it's HTML, create a new HTML file and open it in browser
	                folder_name = clean(subject)
	                if not os.path.isdir(folder_name):
	                    os.mkdir(folder_name) #Make a folder for this email (named after the subject)
	                filename = "index.html"
	                filepath = os.path.join(folder_name, filename) 
	                open(filepath, "w").write(body) #Write the file
	                webbrowser.open(filepath) #Open in the default browser
	            print("="*100)
	            conn = connect('maildatabase.db')
	            c = conn.cursor()
	            try:
	            	c.execute("SELECT * FROM emails where account=? and sender=? and receiver=? and subject=? and message=? and attachment=?", (username,From,username,subject,body,"nofile"))
	            	r=c.fetchone()
	            	if (r==None):
	            		c.execute("INSERT INTO emails(account, sender, receiver, subject, message, attachment) VALUES(?,?,?,?,?,?)", (username, From, username, subject, body, "nofile"))
	            		conn.commit()
	            	else:
	            		print("The emails are already in your database. Take a bigger number of last messages.")
	            except:
	            	print("An error occured.")
	            c.close()
	            conn.close()
	server.close() #Close the connection and logout
	server.logout()



#2) Secure transmission by an end-to-end encryption algorithm
def encrypt(plaintext, key): 
    #Create a Fernet block and use it for encryption.
    fblock = Fernet(key)
    return fblock.encrypt(bytes(plaintext))

def decrypt(ciphertext, key): #To decrypt a ciphertext with the key
    fblock = Fernet(key)
    return fblock.decrypt(bytes(ciphertext))

def generateFernetKey():
    #Generate the fernet key and put it through a KDF (for AES cipher compability)
    salt = os.urandom(16)
    fernet_key = Fernet.generate_key()
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    fernet_key = kdf.derive(fernet_key)
    return fernet_key

def sendMailEncrypted(): #To send an email with the message encrypted (the key will be in the subject)
	case = input("Have you already your account registered ? \n0 = Yes / 1 = No (to register and connect to it)\n")
	if (case=="0"):
		username = input("Enter your mail : ")
		conn = connect("maildatabase.db")
		cur = conn.cursor()
		try:
			cur.execute("SELECT password, smtp_host, smtp_port FROM account where mail=?", (username,))
			r = cur.fetchone()
			password = r[0]
			smtp_ssl_host = r[1]
			smtp_ssl_port = r[2]
			ok = True
			try:
				server = smtplib.SMTP_SSL(smtp_ssl_host, smtp_ssl_port)
				print("The service is securised.")
				server.login(username, password)
				print("You are now connecting to your email server : "+str(smtp_ssl_host))
				keepLogs("Connection to the server realized.")
			except Exception:
				print("One of the field is not correct.")
				keepLogs("Failed to connect to the server.")
			cur.close()
			conn.close()
		except Error:
			ok = False
			cur.close()
			conn.close()
			print("You are not registered or is not that mail.")
	elif (case=="1"):
		smtp_ssl_host = input("Can you enter the smtp_ssl_host of your email server (example for gmail smtp.gmail.com) : ")
		smtp_ssl_port = input("Can you enter the smtp_ssl_port of your email server (choose by default 465) : ")
		username = input("Enter your email : ")
		password = input("Enter your password : ")
		#Check the validity of the format of the 4 entries.
		try:
			server = smtplib.SMTP_SSL(smtp_ssl_host, smtp_ssl_port)
			print("The service is securised.")
			server.login(username, password)
			print("You are now connecting to your email server : "+str(smtp_ssl_host))
			conn = connect("maildatabase.db")
			cur = conn.cursor()
			try:
				cur.execute("INSERT INTO account(mail, password, smtp_host, smtp_port) VALUES(?,?,?,?)", (username, password, smtp_ssl_host, smtp_ssl_port))
				conn.commit()
				print("Your account is registered into the database.")
				cur.close()
				conn.close()
				keepLogs("Connection to the server and adding the account to the database realized.")
			except Error:
				print("An error has occured in registering your account into the database.")
				keepLogs("Failed to connect to the server.")
		except Exception:
			print("One of the field is not correct.")
	targets = []
	while True:
		target = input("Enter the target(s) of your email (if it's finished, write Stop) : ")
		targets.append(target)
		if targets[len(targets)-1] == "Stop":
			targets.remove('Stop')
			break
	subject = input("Enter the subject of your email : ")
	msgToEncrypt = bytes(input("Enter your message to encrypt : "), encoding='utf8')#we ask the message to encrypt, and put it in bytes
	key = Fernet.generate_key() #We generate a fernet key
	f = Fernet(key) #We use the fernet function for the key
	encryptedMessage = f.encrypt(msgToEncrypt) #We encrypt the message with the fernet function that has the key (to encrypt with the key)
	msg = MIMEText(str(encryptedMessage)) #After, we do the same that question 5 to send an basic email
	msg['Subject'] = subject+str(key)
	msg['From'] = username
	msg['To'] = ', '.join(targets)
	server.sendmail(username, targets, msg.as_string()) #Send the mail
	print("The message encrypted has been sent.")
	server.quit() #Terminate
	keepLogs("A message encrypted has been sent.")


def displayCommands(): #Here the function that displays the menu.
	print("\nWelcome to the menu.")
	print("1 = Connect to your mail server(s).")
	print("2 = Add an account to the database without connecting to the account.")
	print("3 = Retrieve emails from the database.")
	print("4 = Read email(s) from one your mail server.")
	print("5 = Send email via one of your mail server.")
	print("6 = Sort your emails by (From, To, Subject).")
	print("7 = See the logs of connections to the mail server (login, @IP, date, etc).")
	print("8 = Save emails to a file.")
	print("9 = Orignal feature.")
	print("10 = Send email with attachments via one of your mail server.")
	print("11 = Send email encrypted via an end-to-end encryption.")
	print("12 = Disconnect.")

def init(): #Here, we init the database with some mails if it's empty, and create the 3 tables : account, logs and emails if your database is not already created.
	conn = connect('maildatabase.db')
	c = conn.cursor()
	c.execute("CREATE TABLE IF NOT EXISTS account(mail TEXT PRIMARY KEY NOT NULL, password TEXT NOT NULL, smtp_host TEXT NOT NULL, smtp_port TEXT NOT NULL)")
	conn.commit()
	c.execute("CREATE TABLE IF NOT EXISTS logs(dateLog DATE NOT NULL, ip TEXT NOT NULL, hostname TEXT NOT NULL, requete TEXT NULL)")
	conn.commit()
	c.execute("CREATE TABLE IF NOT EXISTS emails(id INTEGER NOT NULL PRIMARY KEY, account TEXT NOT NULL, sender TEXT NOT NULL, receiver TEXT NOT NULL, subject TEXT NOT NULL, message TEXT NOT NULL, attachment TEXT NULL, FOREIGN KEY(account) REFERENCES account(mail))")
	conn.commit()
	c.execute("SELECT COUNT(*) from emails")
	result=c.fetchall()
	if result[0][0] == 0:
		c.execute("INSERT INTO emails(id, account, sender, receiver, subject, message, attachment) VALUES(?,?,?,?,?,?,?)", (1, "compte@gmail.com", "compte@gmail.com", "julien@gmail.com", "OK", "Hi, do you have your results?", "nofile"))
		conn.commit()
		c.execute("INSERT INTO emails(id, account, sender, receiver, subject, message, attachment) VALUES(?,?,?,?,?,?,?)", (2, "compte@gmail.com", "compte@gmail.com", "julien@gmail.com", "NO", "when you will get it?", "nofile"))
		conn.commit()
		c.execute("INSERT INTO emails(id, account, sender, receiver, subject, message, attachment) VALUES(?,?,?,?,?,?,?)", (3, "compte@gmail.com", "compte@gmail.com", "julien@gmail.com", "YES", "Okok, "nofile"))
		conn.commit()
	c.close()
	conn.close()

def main(): #Here, it's the choice of which function that we will use and the initialisation.
	init()
	print("Welcome to our server project (mail). Today is : "+str(datetime.datetime.now())+"\nEnter the number corresponding at the command that you want to use.\n")
	number_Command = 0
	while True:
		displayCommands()
		number_Command = input("Can you enter the number corresponding to the command that you want to use?\nNumber of the command : ")
		try:
	   		number_Command = int(number_Command)	
	   		if (number_Command == 1):
		   		connectServer()
		   		
		   	elif (number_Command == 2):
		   		addAccount()
		   	elif (number_Command == 3):
		   		retrieveEmails()
		   	elif (number_Command == 4):
		   		readMailsAndAttachment()
		   	elif (number_Command == 5):
		   		sendMail()
		   	elif (number_Command == 6):
		   		sortEmails()
		   	elif (number_Command == 7):
		   		displayLogs()
		   	elif (number_Command == 8):
		   		savingsEmails()
		   	elif (number_Command == 9):
		   		originalFeature()
		   	elif (number_Command == 10):
		   		q10()
		   	elif (number_Command == 11):
		   		sendMailEncrypted()
		   	elif(number_Command == 12):
		   		print("You have been disconnected from the server.")
		   		break

		except ValueError:
	   		try:
	   			number_Command = float(number_Command)
	   			print("Input is a float  number. Number = " + str(number_Command))
	   		except ValueError:
	   			print("Input is not a number. It's a string")


if __name__ == "__main__":
	main()