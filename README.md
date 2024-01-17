# sysinfo.py
A system info script based on Python, to poll info about a Linux-based system. Uses minimal imports not included in most major Linux Distros. 

![image](img/example.png)

## Dependencies 
`python3-psutil`

`sudo cp /sys/class/dmi/id/product_serial /home/`
`sudo chown <username>: /home/product_serial`

## Raspberry Pi & Systems Without Some DMI Class Info
The sysinfo-raspi.py script is compatible with systems that do not have some dmi class information available. 

## TODO
 - Work around DMI Class info missing on some devices. 
 - Create a Python Script for use in Windows.  
