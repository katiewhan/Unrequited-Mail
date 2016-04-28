import imaplib, email, getpass, time, sys
from email.utils import parsedate
from email.header import decode_header

def strip(string):
    return string.replace('\t', ' ').replace('\r\n', ' ').replace('\n', ' ')

def decode(inp):
    if isinstance(inp, str):
        return strip(inp)
    else:
        return strip(inp.decode('UTF-8'))

def format(msg):
    dh = decode_header(str(msg))
    return ''.join([decode(t[0]) for t in dh]) + "\t"

# Email settings
imap_server = 'imap.gmail.com'
imap_user = 'katie_han@brown.edu'
imap_password = getpass.getpass()

# Connection
conn = imaplib.IMAP4_SSL(imap_server)
(retcode, capabilities) = conn.login(imap_user, imap_password)

# Specify email folder
# print (conn.list())
# conn.select("INBOX.Sent Items")
conn.select('"[Gmail]/All Mail"', readonly=True)   # Set readOnly to True so that emails aren't marked as read

# Search for email ids between dates specified
# result, data = conn.uid('search', None, 'ALL')
result, data = conn.uid('search', None, '(SINCE "01-Jan-2016")')
# result, data = conn.uid('search', None, '(BEFORE "01-Jan-2014")')
# result, data = conn.uid('search', None, '(TO "user@example.org" SINCE "01-Jan-2014")')
i = len(data[0].split())

raw_file = open('email-2016-final.tsv', 'w')
raw_file.write("Message-ID\tDate\tFrom\tTo\tCc\tSubject\tIn-Reply-To\tBody\n")

print("Looping")

for x in range(i):
    latest_uid = data[0].split()[x]

    result, email_data = conn.uid('fetch', latest_uid, '(RFC822)')
    raw_email = email_data[0][1].decode('UTF-8')

    email_message = email.message_from_string(raw_email)

    # HEADERS
    if 'message-id' in email_message:
        row = format(email_message['message-id'])

        timefloat = time.mktime(parsedate(email_message['date']))
        timestamp = str(timefloat) + "\t"
        row += timestamp

        row += format(email_message['from'])
        row += format(email_message['to'])
        row += format(email_message['cc'])
        row += format(email_message['subject'])
        row += format(email_message['in-reply-to'])

        for part in email_message.walk():
            if part.get_content_type() == 'text/plain':
                body = strip(str(part.get_payload()))
                row += body
            else:
                continue

        raw_file.write(row + "\n")

# Done with file, so close it
raw_file.close()
