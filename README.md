### A4 Unrequited Mail 

Using my email data from 2016 (my emailing habits were very different in the past, especially since I studied abroad last semester), I extracted five features: `(average reply time for the sender + average reply time overall) / 2`, ratio of `number of emails replied : total number of emails from the sender`, hour of the day when email was received, character length of email, and whether the To or CC fields contains my email. I used these features to train a linear regression model, which then was able to predict my response time for new incoming emails. I set up Mailbot so that the program drafted a response time prediction email whenever an unread email was detected in my inbox. I also programmed an email assistant that drafts a sample response for the emails. I first check if there are similar emails from the sender in the past, and if there are multiple, find the one with the most overlapping words. Then, I copy and past the text into the draft. Otherwise, if no previous email exchange exists with the sender, I provide a generic template addressed to the sender.

`train-email.py` file contains all of the functionalities described above. It uses the two tsv files in the root directory. The script I used to pull my email data is inside `other_scripts/`.

My program is hosted on an AWS server with a cron job that runs every minute.
