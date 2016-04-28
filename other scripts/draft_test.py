import imaplib
import time
import email.message
import imaplib_connect
import getpass

new_message = email.message.Message()
new_message.set_unixfrom('pymotw')
new_message['Subject'] = 'subject goes here'
new_message['From'] = 'katie_han@brown.edu'
new_message['To'] = 'jimmy_xia@brown.edu'
new_message.set_payload('This is the body of the message.\n')

print(new_message)

# Email settings
imap_server = 'smtp.gmail.com'
imap_user = 'katie_han@brown.edu'
imap_password = getpass.getpass()

# Connection
c = imaplib.IMAP4_SSL(imap_server)

(retcode, capabilities) = c.login(imap_user, imap_password)
try:
    print(c.list())
    c.append('[Gmail]/Drafts', '', imaplib.Time2Internaldate(time.time()), str(new_message).encode('UTF-8'))
    
    # c.select('INBOX')
    # typ, [msg_ids] = c.search(None, 'ALL')
    # for num in msg_ids.split():
    #     typ, msg_data = c.fetch(num, '(BODY.PEEK[HEADER])')
    #     for response_part in msg_data:
    #         if isinstance(response_part, tuple):
    #             print('\n%s:' % num)
    #             print(response_part[1])
finally:
    try:
        c.close()
    except:
        pass
    c.logout()