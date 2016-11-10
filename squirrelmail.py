import subprocess
import fileinput

def squirrelmail(dname):
    """Automations of Sam Hobbs's tutorial for making a Raspberry Pi email server, part 3 (SquirrelMail).
        https://samhobbs.co.uk/2013/12/raspberry-pi-email-server-part-3-squirrelmail"""
    
    
    #Install Apache.
    subprocess.call(['apt-get', 'update'])
    subprocess.call(['apt-get', 'install', 'apache2'])
    
    #Enable the SSL apache module so that you can use HTTPS.
    subprocess.call(['a2enmod', 'ssl'])
    
    #Enable the "default-ssl" virtualhost, by creating a symbolic link.
    subprocess.call(['a2ensite', 'default-ssl'])
    
    #Now reload apache to make the changes take effect.
    subprocess.call(['service', 'apache2', 'reload'])
    
    #Install SquirrelMail.
    subprocess.call(['apt-get', 'update'])
    subprocess.call(['apt-get', 'install', 'squirrelmail'])
    
    #Choose these option on the coming up screen
    print("""
    ############################################
    
    On the next screen choose option "D".
    Then type "dovecot" and hit enter.
    Then press S then enter to save.
    And finally press Q and then enter to quit.
    
    #############################################
""")
    #Wait for the user to read this.
    wait = input("Press enter when ready to continue.")
    
    #Run the basic configuration script for squirrelmail.
    subprocess.call(['squirrelmail-configure'])

    #Create a symbolic link so that Apache2 will load your Squirrelmail apache configuration file when it starts up.
    subprocess.call(['ln','-s','/etc/squirrelmail/apache.conf', '/etc/apache2/conf-enabled/squirrelmail.conf'])
    
    #Reload Apache.
    subprocess.call(['service', 'apache2', 'reload'])
    
    #Configure an HTTPS-only website
    #First backup the apache.conf file
    with fileinput.FileInput('/etc/squirrelmail/apache.conf', inplace=True, backup='.backup') as f:
        for line in f:
            print(line.replace('', ''), end='')

    #Then replace the file with the following
    #Later the example.com, snakeoil cetificate and key files have to be replaced with user's
    with open("/etc/squirrelmail/apache.conf", "w") as f:
        f.write("""
Alias /squirrelmail /usr/share/squirrelmail

#=========================== HTTP redirect to HTTPS ==================================

<VirtualHost *:80>
ServerName webmail.example.com
<IfModule mod_rewrite.c>
  <IfModule mod_ssl.c>
    <Location />
      RewriteEngine on
      RewriteCond %{HTTPS} !^on$ [NC]
      RewriteRule . https://%{HTTP_HOST}%{REQUEST_URI}  [L]
    </Location>
  </IfModule>
</IfModule>
</VirtualHost>

#================================ SQUIRRELMAIL =====================================

<IfModule mod_ssl.c>
<VirtualHost *:443>
  DocumentRoot /usr/share/squirrelmail
  ServerName webmail.example.com

<Directory /usr/share/squirrelmail>
  Options FollowSymLinks
  <IfModule mod_php5.c>
    php_flag register_globals off
  </IfModule>
  <IfModule mod_dir.c>
    DirectoryIndex index.php
  </IfModule>

  # access to configtest is limited by default to prevent information leak
  <Files configtest.php>
    order deny,allow
    deny from all
    allow from 127.0.0.1
  </Files>
</Directory>

ErrorLog ${APACHE_LOG_DIR}/squirrelmail_error.log
LogLevel warn
CustomLog ${APACHE_LOG_DIR}/squirrelmail_ssl_access.log combined

SSLEngine on
SSLCertificateFile /etc/ssl/certs/ssl-cert-snakeoil.pem
SSLCertificateKeyFile /etc/ssl/private/ssl-cert-snakeoil.key

</VirtualHost>
</IfModule>
""")

    #Replace example.com with users actual domain name.
    with fileinput.FileInput('/etc/squirrelmail/apache.conf', inplace=True) as f:
        for line in f:
            print(line.replace('example.com', dname), end='')
    
    #Enable the rewrite module.
    subprocess.call(['a2enmod', 'rewrite'])
    
    #Reload Apache.
    subprocess.call(['service', 'apache2', 'reload'])
    
    #To customise the login page, run the configuration wizard.
    print("""
        #####################################################################
        
        Do the following on the next screen.
        1.Select “1″ (organisation preferences)
        2.Select “7″ and change to your domain (e.g. https://www.arta.space)
        3.Select “8″ and change to you/your organisation’s name.
        
        #####################################################################
        """)
        
    #Wait for the user to read this.
    wait = input("Press enter when ready to continue.")
    
    subprocess.call(['squirrelmail-configure'])
    
    #Install the lockout package for the squirrelmail plugin
    subprocess.call(['apt-get', 'update'])
    subprocess.call(['apt-get', 'install', 'squirrelmail-compatibility'])
    
    print("""
        #########################################
    
        Now we need to enable the plugin:
        On the next screen choose the following:
        1. select “8″
        2. select “compatibility”
        3. select “S” (to save)
        4. select “Q” (to quit)
        
        #########################################
        """)
        
    #Wait for the user to read this.
    wait = input("Press enter when ready to continue.")
    
    subprocess.call(['squirrelmail-configure'])
    subprocess.call(['apt-get', 'install', 'squirrelmail-lockout'])
    
    #Make a back up file of lockout-config.php
    with fileinput.FileInput('/etc/squirrelmail/lockout-config.php', inplace=True, backup='.backup') as f:
        for line in f:
            print(line.replace('', ''), end='')
    
    #Disable logins for the user "admin".
    with open("/etc/squirrelmail/lockout-table.php", "a") as f:
        f.write("\nuser:		admin		locked_out.php")
        
    #Turn on lockouts.
    with fileinput.FileInput('/etc/squirrelmail/lockout-config.php', inplace=True) as f:
        for line in f:
            print(line.replace('$use_lockout_rules = 0;', '$use_lockout_rules = 1;'), end='')

    #We can also lock out IP addresses of users who enter incorrect username/password combinations repeatedly.
    #Data on current bad login attempts and bans is stored 
    #here: /var/lib/squirrelmail/data/lockout_plugin_login_failure_information.
    with fileinput.FileInput('/etc/squirrelmail/lockout-config.php', inplace=True) as f:
        for line in f:
            print(line.replace('max_login_attempts_per_IP = \'\';', 'max_login_attempts_per_IP = \'3:5:0\';'), end='')

