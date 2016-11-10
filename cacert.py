import subprocess
import fileinput

def cacert():
    """Get a new certificate from CAcert.org."""
    
    name = input("What's your name?\n")
    
    #Generate a private key.
    wait = input("Generate a private key. Press enter.")
    
    subprocess.call(['openssl', 'genrsa', '-out', name+'private.key', '4096'])

    #Generate a certificate signing request.
    print("""
    ####################################################################################################################
    
    On the next Screen answer the required fields.
    Here is the information you will be asked for:
        
    Country Name (use a two letter code e.g. CA)
    State or Province Name (e.g. Alberta)
    Locality Name (e.g. Calgary)
    Organisational Name (e.g. Arta's Personal Website)
    Organisational Unit Name (e.g. Website)
    Common Name (your domain name - see note below - e.g. *.arta.space)
    Email Address (the contact address for your administrator e.g. webmaster@arta.space) 

    Don't set a password - leave it blank when asked.
    We will keep the key file private by setting appropriate permissions.

    The common name is important here: most websites rewrite https:// to https://www. or vice versa. 
    If your website is available at https://yourdomain.com then you should use yourdomain.com as the common name;
    if your website is at https://www.yourdomain.com then your common name should be www.yourdomain.com or *.yourdomain.com
    (the wildcard will match any subdomain, meaning you can use the same cert for https://mail.yourdomain.com
    and https://www.yourdomain.com, which is handy).
    
    #########################################################################################################################
    """)

    wait = input("Generate a new certificate signing request (CSR) from your private key. Press enter.")

    #Generate a new certificate signing request (CSR) from your private key.
    subprocess.call(['openssl', 'req', '-new', '-key', name+'private.key', '-out', name+'CSR.csr'])

    
    print("""
    ###############################################################
    
    Open a new terminal on your machine and type the following to
    install the CAcert root certificate.
    
    cd ~
    wget http://www.cacert.org/certs/root.txt
    sudo cp root.txt /etc/ssl/certs/cacert-root.crt
    
    c_rehash /etc/ssl/certs
    
    ################################################################
    """)
    
    wait = input("When ready hit enter")
    
    #Add these aliases to recieve CAcert verification through email
    with open("/etc/aliases", "w") as f:
        f.write("# See man 5 aliases for format.")
        f.write("\npostmaster:    "+name)
        f.write("\nwebmaster:    "+name)
        f.write("\nroot:    "+name)

    #Load the new aliases.
    subprocess.call(['newaliases'])
    
    #Reload Postfix.
    subprocess.call(['service', 'postfix', 'reload'])

    print("""
    ##########################################################################
    
    After you have created your account on CAcert.org and logged in, 
    first navigate to Domains --> Add and add your new domain (eg arta.space)
    and then after you have verified the ownership of your domain via email
    navigate to "server certificates --> new".
    
    Copy & paste the following Certificate Signing Request (CSR) into the box
    and click submit.
    
    ##########################################################################
    """)
    
    wait = input("When ready hit enter.\n")

    #Copy the content of the CSR
    subprocess.call(['cat', name+'CSR.csr'])
    
    wait = input("\nWhenever you have aquired your certificate content hit enter.\n")

    #Copy the result to a CRT file
    print("""
    #############################################################################################
    
    The result will be displayed on screen, and you will also be emailed the certificate.
    Note: the BEGIN CERTIFICATE and END CERTIFICATE lines are part of the cert, so copy those too!
    Copy the certificate content and paste them when presented with an open file. After pasting
    use CTRL+X to save and exit.
    
    ##############################################################################################
    """)
    wait = input("When ready hit enter.")

    #Save the crt to a file
    subprocess.call(['nano', name+'CRT.crt')

    #Move the files to the proper locations.
    subprocess.call(['mv', name+'private.key', '/etc/ssl/private/{keyfile}private.key'.format(keyfile=name)])
    subprocess.call(['mv', name+'CRT.crt', '/etc/ssl/certs/{crtfile}CRT.crt'.format(crtfile=name)])
    
    #Set keyfile to be owned by root.
    subprocess.call(['chown', 'root:root', '/etc/ssl/private/{keyfile}private.key'.format(keyfile=name)])
    
    #Only the root user can read and modify the keyfile.
    subprocess.call(['chmod', '600', '/etc/ssl/private/{keyfile}private.key'.format(keyfile=name)])

    #Set crtfile to be owned by root.
    subprocess.call(['chown', 'root:root', '/etc/ssl/certs/{crtfile}CRT.crt'.format(crtfile=name)])
    
    #Set it to be readable by everyone, but only modified by root.
    subprocess.call(['chmod', '644', '/etc/ssl/certs/{crtfile}CRT.crt'.format(crtfile=name)])

    #Put the files in apache default-ssl
    with open("/etc/apache2/sites-available/default-ssl.conf", "w") as f:
        f.write("""

<IfModule mod_ssl.c>
NameVirtualHost *:443

#=============================== ANTI SPAM ================================
<VirtualHost *:443>
        ServerName default.only
        <Location />
                Order allow,deny
                Deny from all
        </Location>

        SSLEngine on
        SSLCertificateFile /etc/ssl/certs/certfile.crt
        SSLCertificateKeyFile /etc/ssl/private/keyfile.key
</VirtualHost>

#================================ WEBSITE ===================================

<VirtualHost *:443>
        ServerAdmin webmaster@rajabi.ca
        ServerName www.rajabi.ca
        ServerAlias rajabi.ca

        DocumentRoot /var/www/html/

        <Directory /var/www/html/>
                Options Indexes FollowSymLinks MultiViews
                AllowOverride all
                Order allow,deny
                allow from all
        </Directory>

        ErrorLog ${APACHE_LOG_DIR}/error.log
        LogLevel warn
        CustomLog ${APACHE_LOG_DIR}/ssl_access.log combined

        SSLEngine on
        SSLCertificateFile /etc/ssl/certs/certfile.crt
        SSLCertificateKeyFile /etc/ssl/private/keyfile.key

        <FilesMatch "\.(cgi|shtml|phtml|php)$">
                SSLOptions +StdEnvVars
        </FilesMatch>
        <Directory /usr/lib/cgi-bin>
                SSLOptions +StdEnvVars
        </Directory>

        BrowserMatch "MSIE [2-6]" \
                nokeepalive ssl-unclean-shutdown \
                downgrade-1.0 force-response-1.0
        # MSIE 7 and newer should be able to use keepalive
        BrowserMatch "MSIE [17-9]" ssl-unclean-shutdown
</VirtualHost>

#============================= SECOND WEBSITE ================================
""")

    #Replace certfile and keyfile in apache's default-ssl with the correct files.
    with fileinput.FileInput('/etc/apache2/sites-available/default-ssl.conf', inplace=True, backup='.backup') as f:
        for line in f:
            print(line.replace('certfile.crt', name+'CRT.crt'), end='')
            
    with fileinput.FileInput('/etc/apache2/sites-available/default-ssl.conf', inplace=True, backup='.backup') as f:
        for line in f:
            print(line.replace('keyfile.key', name+'private.key'), end='')

    #Replace certfile and keyfile in Postfix's main.cf with the correct files.
    with fileinput.FileInput('/etc/postfix/main.cf', inplace=True) as f:
        for line in f:
            print(line.replace('ssl-cert-snakeoil.pem', name+'CRT.crt'), end='')
    
    with fileinput.FileInput('/etc/postfix/main.cf', inplace=True) as f:
        for line in f:
            print(line.replace('ssl-cert-snakeoil.key', name+'private.key'), end='')

    #Replace certfile and keyfile in Dovecot's 10-ssl.conf with the correct files.
    with fileinput.FileInput('/etc/dovecot/conf.d/10-ssl.conf', inplace=True) as f:
        for line in f:
            print(line.replace('/etc/dovecot/dovecot.pem', '/etc/ssl/certs/'+name+'CRT.crt'), end='')
    
    with fileinput.FileInput('/etc/dovecot/conf.d/10-ssl.conf', inplace=True) as f:
        for line in f:
            print(line.replace('/etc/dovecot/private/dovecot.pem', '/etc/ssl/private/'+name+'private.key'), end='')

    #Replace certfile and keyfile in Squirrelmail apache.conf with the correct files.
    with fileinput.FileInput('/etc/squirrelmail/apache.conf', inplace=True) as f:
        for line in f:
            print(line.replace('ssl-cert-snakeoil.pem', name+'CRT.crt'), end='')
    
    with fileinput.FileInput('/etc/squirrelmail/apache.conf', inplace=True) as f:
        for line in f:
            print(line.replace('ssl-cert-snakeoil.key', name+'private.key'), end='')

    subprocess.call(['service', 'postfix', 'reload'])
    subprocess.call(['service', 'dovecot', 'reload'])
    subprocess.call(['service', 'apache2', 'reload'])
            
cacert()
