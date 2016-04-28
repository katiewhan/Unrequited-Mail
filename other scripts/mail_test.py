from mailbot import MailBot, register, Callback
from pprint import pprint
import getpass

class MyCallback(Callback):
	#rules = {'subject': ['lol'], 'from': [r'@brown.edu']}

	def trigger(self):
		print(self.message.keys())
		print(self.message.values())
		#print("Mail received for {0}".format(self.matches['from'][0]))

mailbot = MailBot('imap.gmail.com', 'katie_han@brown.edu', getpass.getpass(), port=993, ssl=True)

register(MyCallback)
mailbot.process_messages()