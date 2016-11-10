import subprocess
import fileinput

def lmtp_sieve(name, dname):
    """Automations of Sam Hobbs's tutorial for making a Raspberry Pi email server, part 5 (LMTP & Sieve).
        https://samhobbs.co.uk/2014/03/raspberry-pi-email-server-part-5-spam-sorting-with-lmtp-sieve"""

    #Install dovecot-lmtpd.
    subprocess.call(['apt-get', 'update'])
    subprocess.call(['apt-get', 'install', 'dovecot-lmtpd'])

    #Back up dovecot.conf.
    with fileinput.FileInput('/etc/dovecot/dovecot.conf', inplace=True, backup='.backup') as f:
        for line in f:
            print(line.replace('', ''), end='')
        
    #Enable LMTP in dovecot.
    with open("/etc/dovecot/dovecot.conf", "a") as f:
        f.write("\nprotocols = imap lmtp")

    #Enable address extensions.
    with fileinput.FileInput('/etc/dovecot/conf.d/20-lmtp.conf', inplace=True, backup='.backup') as f:
        for line in f:
            print(line.replace('#lmtp_save_to_detail_mailbox = no', 'lmtp_save_to_detail_mailbox = yes'), end='')

    #Now change the lmtp protocol block.
    with fileinput.FileInput('/etc/dovecot/conf.d/20-lmtp.conf', inplace=True) as f:
        for line in f:
            print(line.replace('protocol lmtp {',
                "protocol lmtp {\n"
    +"\tmail_plugins = $mail_plugins sieve\n"
    +"\tpostmaster_address = postmaster@{thisdname}".format(thisdname=dname)), end='')

    #This will allow postfix to access Dovecot’s LMTP from within its chroot.
    with fileinput.FileInput('/etc/dovecot/conf.d/10-master.conf', inplace=True, backup='.backup') as f:
        for line in f:
            print(line.replace('unix_listener lmtp {',
"""     unix_listener /var/spool/postfix/private/dovecot-lmtp {
          mode = 0666"""), end='')

    #This setting instructs Dovecot to strip the domain name before doing the lookup, and convert the username to all lowercase letters.
    with fileinput.FileInput('/etc/dovecot/conf.d/10-auth.conf', inplace=True, backup='.backup') as f:
        for line in f:
            print(line.replace('#auth_username_format = %Lu', 'auth_username_format = %Ln'), end='')

    #Instruct Postfix to hand over control to Dovecot’s LMTP for the final stage of delivery.
    with open("/etc/postfix/main.cf", "a") as f:
        f.write("\nmailbox_transport = lmtp:unix:private/dovecot-lmtp")

    #Install dovecot-sieve.
    subprocess.call(['apt-get', 'update'])
    subprocess.call(['apt-get', 'install', 'dovecot-sieve'])

    #Now we need to change one more parameter in /etc/dovecot/conf.d/90-sieve.conf.
    with fileinput.FileInput('/etc/dovecot/conf.d/90-sieve.conf', inplace=True, backup='.backup') as f:
        for line in f:
            print(line.replace('#recipient_delimiter = +', 'recipient_delimiter = +'), end='')

    #We still need to reload/restart Postfix and Dovecot to make that all the changes are loaded.
    subprocess.call(['service', 'postfix', 'reload'])
    subprocess.call(['service', 'dovecot', 'reload'])

    #The default place to put the sieve script is in the user's home folder: ~/.dovecot.sieve.
    #Make this file and append the following.
    with open("/home/{thisname}/.dovecot.sieve".format(thisname=name), "a") as f:
        f.write("""require ["fileinto"];
# Move spam to spam folder
if header :contains "X-Spam-Flag" "YES" {
  fileinto "Spam";
  # Stop here - if there are other rules, ignore them for spam messages
  stop;
}
""")

    #Now chown the file to the owner of the mailbox.
    subprocess.call(['chown', name+':'+name, '/home/{user}/.dovecot.sieve'.format(user=name)])
