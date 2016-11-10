import subprocess
import fileinput

def dovecot():
    """Automations of Sam Hobbs's tutorial for making a Raspberry Pi email server, part 2 (Dovecot).
        https://samhobbs.co.uk/2013/12/raspberry-pi-email-server-part-2-dovecot"""
    
    
    #Tell Dovecot where your mailbox is
    with fileinput.FileInput('/etc/dovecot/conf.d/10-mail.conf', inplace=True, backup='.backup') as f:
        for line in f:
            print(line.replace('mail_location = mbox:~/mail:INBOX=/var/mail/%u', 'mail_location = maildir:~/Maildir'), end='')

    #Tell postfix to use Dovecot for SASL authintication.
    with open("/etc/postfix/main.cf", "a") as f:
        f.write("""
smtpd_sasl_type = dovecot
smtpd_sasl_path = private/auth
smtpd_sasl_auth_enable = yes
""")

    #Now tell Dovecot to listen for SASL authentication requests from Postfix.
    with fileinput.FileInput('/etc/dovecot/conf.d/10-master.conf', inplace=True, backup='.backup') as f:
        for line in f:
            print(line.replace('unix_listener auth-userdb {', 'unix_listener /var/spool/postfix/private/auth {\n'
                +'\tmode = 0660\n'
                +'\tuser = postfix\n'
                +'\tgroup = postfix\n'), end='')

    #Now you want to enable plain text logins.
    with fileinput.FileInput('/etc/dovecot/conf.d/10-auth.conf', inplace=True, backup='.backup') as f:
        for line in f:
            print(line.replace('#disable_plaintext_auth = yes', 'disable_plaintext_auth = no\n'), end='')
            
    with fileinput.FileInput('/etc/dovecot/conf.d/10-auth.conf', inplace=True) as f:
        for line in f:
            print(line.replace('auth_mechanisms = plain', 'auth_mechanisms = plain login\n'), end='')

    #Set up Postfix to listen on port 465 for encrypted connections.
    with fileinput.FileInput('/etc/postfix/master.cf', inplace=True, backup='.backup') as f:
        for line in f:
            print(line.replace('#smtps     inet  n       -       -       -       -       smtpd', 'smtps     inet  n       -       -       -       -       smtpd\n'), end='')

    #Now force TLS on port 465.
    with fileinput.FileInput('/etc/postfix/master.cf', inplace=True) as f:
        for line in f:
            print(line.replace('#  -o syslog_name=postfix/smtps',
                '  -o syslog_name=postfix/smtps\n'
                +'  -o smtpd_tls_wrappermode=yes\n'), end='')

    #Tell Postfix to only advertise SASL authentication over encrypted connections 
    #(so that you don’t accidentally send your password in the clear).
    with open("/etc/postfix/main.cf", "a") as f:
        f.write("\nsmtpd_tls_auth_only = yes")

    #Now override the smtp_recipient_restrictions for port 465 so that it doesn't accept incoming messages from unauthenticated users.
    with fileinput.FileInput('/etc/postfix/master.cf', inplace=True) as f:
        for line in f:
            print(line.replace('#  -o smtpd_tls_wrappermode=yes',
                '  -o smtpd_recipient_restrictions=permit_sasl_authenticated,reject\n'), end='')

    #Enable IMAPS (imap with SSL/TLS). The standard port for this is 993.
    with fileinput.FileInput('/etc/dovecot/conf.d/10-master.conf', inplace=True) as f:
        for line in f:
            print(line.replace('#port = 143', 'port = 143'), end='')
            
    with fileinput.FileInput('/etc/dovecot/conf.d/10-master.conf', inplace=True) as f:
        for line in f:
            print(line.replace('#port = 993', 'port = 993\n'+'    ssl = yes'), end='')    

    with fileinput.FileInput('/etc/dovecot/conf.d/10-ssl.conf', inplace=True, backup='.backup') as f:
        for line in f:
            print(line.replace('ssl = no', 'ssl = yes'), end='')
            
    with fileinput.FileInput('/etc/dovecot/conf.d/10-ssl.conf', inplace=True) as f:
        for line in f:
            print(line.replace('#ssl_protocols = !SSLv2', 'ssl_protocols = !SSLv2 !SSLv3'), end='')

    #Generate temp snakeoil certificate and key files
    subprocess.call(['./mkcert.sh'])
    
    #Use the new certificate and key file
    with fileinput.FileInput('/etc/dovecot/conf.d/10-ssl.conf', inplace=True) as f:
        for line in f:
            print(line.replace('#ssl_cert = </etc/dovecot/dovecot.pem', 'ssl_cert = </etc/dovecot/dovecot.pem'), end='')
            
    with fileinput.FileInput('/etc/dovecot/conf.d/10-ssl.conf', inplace=True) as f:
        for line in f:
            print(line.replace('#ssl_key = </etc/dovecot/private/dovecot.pem', 'ssl_key = </etc/dovecot/private/dovecot.pem'), end='')
    
    #Restart Postfix and Dovecot
    subprocess.call(['service', 'postfix', 'restart'])
    subprocess.call(['service', 'dovecot', 'restart'])
