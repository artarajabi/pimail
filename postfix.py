import subprocess
import fileinput

def postfix(name, dname):
    """Automations of Sam Hobbs's tutorial for making a Raspberry Pi email server, part 1 (Postfix).
        https://samhobbs.co.uk/2013/12/raspberry-pi-email-server-part-1-postfix"""
    
    
    #Update system and install Postfix.
    print("""
    ######################################################################
    
    Select "Internet Site" and then set the mail name to your domain name,
    not including www. (e.g. arta.space).
    
    ######################################################################
""")
    
    wait = input("When ready press enter to continue.")
    
    subprocess.call(['apt-get', 'update'])
    subprocess.call(['apt-get', 'install', 'postfix'])

    #Open main.cf and make a backup of it.
    with fileinput.FileInput('/etc/postfix/main.cf', inplace=True, backup='.backup') as f:
        for line in f:
            print(line.replace('', ''), end='')

    #Tell Postfix to use the Maildir format, add the following lines to /etc/postfix/main.cf
    with open("/etc/postfix/main.cf", "a") as f:
        f.write("\nhome_mailbox = Maildir/\n")
        #f.write("\nmailbox_command =")
    
    #Install Dovecot
    subprocess.call(['apt-get', 'update'])
    subprocess.call(['apt-get', 'install', 'dovecot-common', 'dovecot-imapd'])

    #We also need to create the mail directory and its subfolders for existing users, 
    #and add some things to /etc/skel (the template for new users)
    #so that if you create a new account this will be done automatically.
    #Run the following commands to create the template files.
    subprocess.call(['maildirmake.dovecot', '/etc/skel/Maildir'])
    subprocess.call(['maildirmake.dovecot', '/etc/skel/Maildir/.Drafts'])
    subprocess.call(['maildirmake.dovecot', '/etc/skel/Maildir/.Sent'])
    subprocess.call(['maildirmake.dovecot', '/etc/skel/Maildir/.Spam'])
    subprocess.call(['maildirmake.dovecot', '/etc/skel/Maildir/.Trash'])
    subprocess.call(['maildirmake.dovecot', '/etc/skel/Maildir/.Templates'])

    #Next, copy the files over to existing users’ home directories, and change the ownership and permissions for privacy.
    subprocess.call(['cp', '-r', '/etc/skel/Maildir', '/home/' + name + '/'])
    subprocess.call(['chown', '-R', name + ':' + name, '/home/'+name+'/Maildir'])
    subprocess.call(['chmod', '-R', '700', '/home/'+name+'/Maildir'])
        
    #Add the following to /etc/postfix/main.cf to restrict who can send emails to external mail servers:
    with open("/etc/postfix/main.cf", "a") as f:
        f.write("""
smtpd_recipient_restrictions =
        permit_sasl_authenticated,
        permit_mynetworks,
        reject_unauth_destination
""")
        
    #Modify helo access restrictions by adding the following to /etc/postfix/main.cf to block spam.
    with open("/etc/postfix/main.cf", "a") as f:
        f.write("""
smtpd_helo_required = yes
smtpd_helo_restrictions =
        permit_mynetworks,
        permit_sasl_authenticated,
        reject_invalid_helo_hostname,
        reject_non_fqdn_helo_hostname,
        reject_unknown_helo_hostname,
        check_helo_access hash:/etc/postfix/helo_access
""")
        
    #That last line in smtpd_helo_restrictions checks a file for custom rules you’ve built in. Create the file.
    with open("/etc/postfix/helo_access", "a") as f:
        f.write(dname+"          REJECT          Get lost - you're lying about who you are\n")
        f.write("mail."+dname+"      REJECT          Get lost - you're lying about who you are\n")
        f.write("webmail."+dname+"      REJECT          Get lost - you're lying about who you are\n")
    
    #Now tell postfix to map the file, and restart postfix.
    subprocess.call(['postmap', '/etc/postfix/helo_access'])
    subprocess.call(['service', 'postfix', 'restart'])
