from sklearn import linear_model
from sklearn import cross_validation
import numpy as np
import time, getpass, email, imaplib, re
import pandas as pd
from email.utils import parsedate
from email.header import decode_header
from mailbot import MailBot, register, Callback

email_user = 'katie_han@brown.edu'
email_password = getpass.getpass()


# MACHINE LEARNING ON EMAIL DATA WITH LINEAR REGRESSION

df = pd.read_csv('email-2016.tsv', sep='\t', header=None)
df = df.fillna('')
em = df.as_matrix()

df_s = pd.read_csv('email-2016-sent.tsv', sep='\t', header=None)
df_s = df_s.fillna('')
em_s = df_s.as_matrix()

sender_set = set(em[:,2])
reply_to = list(em_s[:,6])
reply_times = {}
reply_time_avg = 0 # calculated below

def feature(email):
	features = []

	# sender index
	if email[2] in reply_times:
		adjusted = (reply_times[email[2]] + reply_time_avg) / 2
		features.append(adjusted)
	else:
		features.append(604800) # arbitrary max time of reply is 1 week

	# ratio of replied to not
	got = len(np.where(em[:,2] == email[2])[0]) +1
	rep = len(np.where(email[2] in em_s[:,3])[0]) +1
	features.append(float(rep)/float(got))

	# hour of the day when email was received
	h = time.localtime(float(email[1]))[3]
	features.append(h)

	# character length of email
	l = len(email[7])
	features.append(l)

	# whether To field contains my email
	r = 'katie_han@brown.edu' in email[3] or 'katie_han@brown.edu' in email[4]
	features.append(int(r))

	return features

def time_calc(email):
	ind = reply_to.index(email[0])
	reply_time = em_s[ind,1]
	sent_time = email[1]
	seconds = float(reply_time) - float(sent_time)
	return seconds

def target(email):
	if email[0] in reply_to:
		return time_calc(email)
	else:
		return 604800

# calculate reply times for each sender and averge overall
count = 0

for s in sender_set:
	times = []
	indices = np.where(em[:,2] == s)
	for i in indices[0]:
		if em[i,0] in reply_to:
			r_time = time_calc(em[i])
			reply_time_avg += r_time
			count += 1
			times.append(r_time)
	if len(times) == 0:
		reply_times[s] = 604800
	else:
		times_np = np.array(times)
		reply_times[s] = np.average(times_np)

reply_time_avg = reply_time_avg / count

# setting up linear regression with reply data as training set
train_data = []
train_target = []

for i in range(0,len(em_s)):
	ids = list(em[:,0])
	x = ids.index(em_s[i,6])
	train_data.append(feature(em[x]))
	train_target.append(target(em[x]))

regr = linear_model.LinearRegression()
regr.fit(train_data, train_target)
print('Linear Regression Coefficients: ')
print(regr.coef_)
print('CV Results: ')
print(cross_validation.cross_val_score(regr, train_data, train_target))


# EMAIL RESPONDER AND ASSISTANT USING MAILBOT AND IMAP

def strip_string(string):
	return string.replace('\t', ' ').replace('\r\n', ' ').replace('\n', ' ')

def decode(inp):
	if isinstance(inp, str):
		return strip_string(inp)
	else:
		return strip_string(inp.decode('UTF-8'))

def format(msg):
	dh = decode_header(str(msg))
	return ''.join([decode(t[0]) for t in dh])

def draft(incoming, response):
	new_message = email.message.Message()
	new_message.set_unixfrom('pymotw')
	new_message['Subject'] = 'Re: ' + incoming[5]
	new_message['From'] = 'katie_han@brown.edu'
	new_message['To'] = incoming[2]
	new_message['In-Reply-To'] = incoming[0]
	new_message.set_payload(response)

	imap_server = 'smtp.gmail.com'
	c = imaplib.IMAP4_SSL(imap_server)
	retcode, capabilities = c.login(email_user, email_password)

	try:
		c.append('[Gmail]/Drafts', '', imaplib.Time2Internaldate(time.time()), str(new_message).encode('UTF-8'))
	finally:
		try:
			c.close()
		except:
			pass
		c.logout()

def draft_response(incoming):
	below = r'On (\w+), (.*), 2016 at (.*) wrote: (.*)'

	word_overlaps = {}
	new_body = set(incoming[7].split())
	sender_indices = np.where(em[:,2] == incoming[2])
	reply_indices = np.where(np.in1d(em[:,0], em_s[:,6]))
	indices = np.intersect1d(sender_indices[0], reply_indices[0])

	auto_res = ""
	if len(indices) == 0:
		auto_res = "Hi " + ''.join(c for c in incoming[2] if c.isalnum() or c.isspace()).split()[0] + """, 

		Thank you getting in touch with me!

		Best,
		Katie Han"""
	else:
		for i in indices:
			old_body = set(em[i,7].split())
			intersect = old_body & new_body
			word_overlaps[len(intersect)] = i
		# choose the most similar email
		index = word_overlaps[max(word_overlaps)]
		reply_i = reply_to.index(em[index,0])
		auto_res = re.sub(below, "", em_s[reply_i,7])

	draft(incoming, auto_res)
	print("Drafted sample reply!")

def draft_time(incoming, expected):
	# only drafts if the expected time is less than 5 days (since max time is 1 week)
	if expected < 120 and expected > 0:
		email_response = ""
		if expected < 24:
			email_response = """Hi there! Thank you for emailing me. According to my email responder 
				(who is supposedly smarter than me with all the machine learning powers), 
				you can expect my response in about """ + "%.2f" % expected + """ hours. Cheers!

				Katie Han

				**This is an auto-generated email."""
		else:
			day = int(expected/24)
			email_response = """Hi there! Thank you for emailing me. According to my email responder 
				(who is supposedly smarter than me with all the machine learning powers), 
				you can expect my response in about """ + str(day) + """ days. Hopefully. Cheers!

				Katie Han

				**This is an auto-generated email."""

		draft(incoming, email_response)
		print("Drafted response prediction!")
		# only draft sample response if it is "worth" replying to
		draft_response(incoming)

class MyCallback(Callback):
	#rules = {'subject': ['lol'], 'from': [r'@brown.edu']}

	def trigger(self):
		email = []
		mess = self.message
		email.append(format(mess['message-id']))

		timefloat = time.mktime(parsedate(mess['date']))
		timestamp = str(timefloat)
		email.append(timestamp)

		email.append(format(mess['from']))
		email.append(format(mess['to']))
		email.append(format(mess['cc']))
		email.append(format(mess['subject']))
		email.append(format(mess['in-reply-to']))

		for part in mess.walk():
			if part.get_content_type() == 'text/plain':
				body = strip_string(str(part.get_payload()))
				email.append(body)
			else:
				continue

		if len(email) < 8:
			email.append('')

		f = feature(email)
		predicted = regr.predict([f])[0]
		draft_time(email, predicted/3600)

mailbot = MailBot('imap.gmail.com', email_user, email_password, port=993, ssl=True)
register(MyCallback)
mailbot.process_messages()