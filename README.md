# pimail
My attempt to automate the process in Sam Hobbs tutorial (https://samhobbs.co.uk/raspberry-pi-email-server) for making a personal email server on Raspberry Pi.

This has to be installed on a Raspberry Pi with a freshly installed Raspbian jessie.

To install:
	1.Copy the files to your Raspberry Pi - sudo scp -r /pass/to/Email_Server/ pi@localIPaddress:/home/pi
	2.Become root - sudo -i
	3.Change into the directory containing the files - cd /home/pi/Email_Server
	4.Run installemailserver.py - python3 installemailserver.py
	5.Follow the on screen instructions and answer everything carefully.
	6.After reboot change into same directory and run - python3 cacert.py
