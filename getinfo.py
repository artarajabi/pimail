import subprocess
import fileinput

def get_user_info():
    """Get user info."""
    
    name = input("What's your name?\n")
    dname = input("What's your domain name?\n")

    #Add this user to the Raspbian
    print("##############################################################")
    print("New user will be added and at the very end of the installation"
        +"\tthe user pi is removed.")
    wait = input("When ready hit enter and answer the required fields.")
    subprocess.call(['adduser', name])
    
    #Once this user has been created, you should add them to some useful groups:
    # sudo so that they have superuser access and
    # adm so that they can read log files without using sudo:
    subprocess.call(['usermod', '-a', '-G', 'sudo', name])
    subprocess.call(['usermod', '-a', '-G', 'adm', name])
    
    #Change Raspbian's hostname
    print("################################################################")
    print("The system's hostname will be changed to the given domain name.")
    wait = input("When ready hit enter to continue.")
    
    with fileinput.FileInput('/etc/hosts', inplace=True, backup='.bak') as f:
        for line in f:
            print(line.replace('raspberrypi', dname), end='')
    
    with fileinput.FileInput('/etc/hostname', inplace=True, backup='.bak') as f:
        for line in f:
            print(line.replace('raspberrypi', dname), end='')
    
    subprocess.call(['/etc/init.d/hostname.sh', 'start'])
    
    #Return these user informations
    infodic = {"name": name, "domain": dname}
    return infodic
