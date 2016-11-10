import getinfo as gi
import postfix as ps
import dovecot as dv
import squirrelmail as sm
import spamassassin as sp
import lmtp_sieve as ls
import subprocess

#Update and Upgrade your machine
subprocess.call(['apt-get', 'update'])
subprocess.call(['apt-get', 'upgrade'])
subprocess.call(['apt-get', 'dist-upgrade'])

#Fort this program to work you need to be root.
#So once you've SSHed into pi you need to type sudo -i
#Give a little info about this program
print("""\

##################################################################################

This program needs to be installed in root on a fresh Raspbian (ie. sudo -i).

A fully working email server needs:
 1.A fully qualified domain name (Perhaps from namecheap.com).
 
 2.Make sure you have a static WAN IP address which you can map your domain
 name to. namecheap.com has a way to automatically forward your domain name
 to your IP address if you have a dynamic IP address instead of a static one.
 
 3.Make sure your Pi has a static LAN IP address and then forward these ports
  from WAN to its LAN IP address:
    Port 25 for SMTP (used for receiving emails)
    Port 465 for secure SMTP (used for sending emails after SASL authentication)
    Port 993 for IMAPS (used to receive emails on your phone/tablet/computer)
    Port 80 for http
    Port 443 for https

 4.In order to securely connect to your email server over the internet a 
 Certificate Authority needs to sign a certificate for your website to be
 verified.(CAcerts provides this service for free).
 Your Certificate file goes in "/etc/ssl/certs/" and your private key file goes
 in "/etc/ssl/private/".
 
 5.Set up your DNS as such:
 
    Type            Host            Value             MX PREF       TTL
    -----------------------------------------------------------------------
    A Record        @               your-WAN-IP                     60min
    A Record        www             your-WAN-IP                     60min
    A Record        webmail         your-WAN-IP                     60min
    TXT Record      @               v=spf1 mx a ~all                60min
    
                                                     
    MX Record       @               yourdomain.com.     10          60min
    
 #################################################################################
 
""")

#Wait for the user to read this.
wait = input("Press enter when ready to continue.")

#Get the user's information and store it in a dictionary
userinfo = gi.get_user_info()

#Extract the fields from that dictionary
name = userinfo["name"]
dname = userinfo["domain"]

#Pass the name and the domain name of the user to the following definitions
ps.postfix(name, dname)
dv.dovecot()
sm.squirrelmail(dname)
sp.spamassassin()
ls.lmtp_sieve(name, dname)

#Run raspi-config
print("""

############################################################################

On the next screen make the following changes:

    Expand the filesystem.
    Internationalisation options: change the locale and timezone.
    Use the advanced options to set the memory allocation for the GPU to 0, 
        since the Pi will be running “headless” (no monitor).
    Finish & reboot.
    
    After rebooting ssh into the new user you created.
    Delete the default user pi using "sudo userdel pi".
    And remove it's home directory using "sudo rm -r /home/pi/".
    
#############################################################################

""")
subprocess.call(['raspi-config'])

wait=input("When ready press enter to continue.")
