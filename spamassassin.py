import subprocess
import fileinput

def spamassassin():
    """Automations of Sam Hobbs's tutorial for making a Raspberry Pi email server, part 4 (Spamassassin).
        https://samhobbs.co.uk/2014/03/raspberry-pi-email-server-part-4-spam-detection-with-spamassassin"""


    #Install Spamassassin.
    subprocess.call(['apt-get', 'update'])
    subprocess.call(['apt-get', 'install', 'spamassassin'])

    #This one will add the spam score to the subject line of emails that Spamassassin considers to be spam.
    with fileinput.FileInput('/etc/spamassassin/local.cf', inplace=True, backup='.backup') as f:
        for line in f:
            print(line.replace('# rewrite_header Subject *****SPAM*****', 'rewrite_header Subject *****SPAM*****'), end='')

    #This next setting will tell Spamassassin to modify headers only, without making any changes to the body of the email.
    with fileinput.FileInput('/etc/spamassassin/local.cf', inplace=True) as f:
        for line in f:
            print(line.replace('# report_safe 1', 'report_safe 0'), end='')
    
    #This one lowers the threshold for mail to be considered spam from 5 to 2.        
    with fileinput.FileInput('/etc/spamassassin/local.cf', inplace=True) as f:
        for line in f:
            print(line.replace('# required_score 5.0', 'required_score 2.0'), end='')
    
    #This tells Spamassassin to use Bayesian filtering.
    with fileinput.FileInput('/etc/spamassassin/local.cf', inplace=True) as f:
        for line in f:
            print(line.replace('# use_bayes 1', 'use_bayes 1'), end='')
    
    #This turns on automatic learning.        
    with fileinput.FileInput('/etc/spamassassin/local.cf', inplace=True) as f:
        for line in f:
            print(line.replace('# bayes_auto_learn 1', 'bayes_auto_learn 1'), end='')

    #Enable Spamassassin.
    with fileinput.FileInput('/etc/default/spamassassin', inplace=True, backup='.backup') as f:
        for line in f:
            print(line.replace('ENABLED=0', 'ENABLED=1'), end='')

    #Now restart Spamassassin
    subprocess.call(['service', 'spamassassin', 'start'])

    #At this stage, the Spamassassin daemon is running but none of your incoming emails are being passed through it.        
    with fileinput.FileInput('/etc/postfix/master.cf', inplace=True) as f:
        for line in f:
            print(line.replace('smtp      inet  n       -       -       -       -       smtpd',
                """smtp      inet  n       -       -       -       -       smtpd
    -o content_filter=spamassassin"""), end='')

    #And append this to the bottom of that same file,
    #which will pipe the output back to Postfix using the Postfix’s Sendmail compatibility interface
    with open("/etc/postfix/master.cf", "a") as f:
        f.write("\nspamassassin    unix  -       n       n       -       -       "
            +"pipe user=debian-spamd argv=/usr/bin/spamc -f -e /usr/sbin/sendmail"
            +" -oi -f ${sender} ${recipient}")

    #Now restart Postfix
    subprocess.call(['service', 'postfix', 'restart'])

    #We’ve deliberately set the score limit for spam to a low value.
    #This inevitably means we’ll get some false positives, but we can use these
    # to train Spamassassin and make it better.
    with open("/etc/cron.daily/spamassassin-learn", "w") as f:
        f.write("""#!/bin/bash
 
# Script by Sam Hobbs https://samhobbs.co.uk
 
# redirect errors and output to logfile
exec 2>&1 1>> /var/log/spamassassin.log
 
NOW=$(date +"%Y-%m-%d")
 
# Headers for log
echo ""
echo "#================================ $NOW ================================#"
echo ""
 
# learn HAM
echo "Learning HAM from Inbox"
sa-learn --no-sync --ham /home/sam/Maildir/{cur,new}
 
# learn SPAM
echo "Learning SPAM from Spam folder"
sa-learn --no-sync --spam /home/sam/Maildir/.Spam/{cur,new}
 
# Synchronize the journal and databases.
echo "Syncing"
sa-learn --sync
""")

    #Now make the script executable.
    subprocess.call(['chmod', '+x', '/etc/cron.daily/spamassassin-learn'])
