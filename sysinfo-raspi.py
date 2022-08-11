#!/usr/bin/env python3

"""
Author: Jonathan E. Rux
Last Updated: 2022/04/20
System Information Script in Python. If you have any ideas of things that can be added with the imports included, feel free to send recommendations. 

Nonstandard Libraries to Ubuntu: python3-psutil 
"""

import os, subprocess as sp, psutil as psu, socket as s, time as t, platform as plat, math, cpuinfo
from posixpath import split

# --------------------------------- #
#         Utility Functions         #
# --------------------------------- #

# Quick Function to deal with Opening and Reading File Contents
def readFile(f):
    fo=open(f)
    cont=fo.read()[:-1]
    fo.close()
    return cont

# Checks if the system is a Physical system or Virtual Machine.
def checkHypervisor():
    virtual=True
    check=os.popen('lscpu | grep -i "Hypervisor vendor"').read()[:-1]
    if check == '':
        virtual=False
    #Return Value
    if virtual==True:
        return "Virtual Machine"
    else:
        return "Physical"

# Checks if disk usage for /home is above a threshold.
# Note: Change threshold value to hide disk usage section
# when less than percentage. 
def diskUsageHigh():
    threshold=0
    usage=psu.disk_usage("/home")
    if int(usage[3]) >= threshold:
        return True

# Get Memory for each GPU and return it.
def gpuMemory(id):
    lines=[]
    for address in id:
        if address != "": # Checks for Empty Indexes
            mem=os.popen(f"lspci -v -s {address} | grep Memory").read()[:-1].split("\n")
            for each in enumerate(mem):
                if each == "":
                    each="none"
                    lines.append(each[1])
                else:
                    lines.append(each[1])    
    return lines


# Get kernel driver for each GPU and return it.
def gpuKernelDriver(id):
    lines=[]
    for address in id:
        if address != "": # Checks for Empty Indexes
            driver=os.popen(f"lspci -k -s \"{address}\" | grep \"Kernel driver\" | cut -d \":\" -f2").read()[1:-1].split("\n")
            for each in enumerate(driver):
                if each[1] == "":
                    empty="none"
                    lines.append(empty)
                else:
                    lines.append(each[1])          
    return lines

def gpuKernelMod(id):
    lines=[]
    for address in id:
        if address != "":
            module=os.popen(f"lspci -k -s \"{address}\" | grep \"Kernel module\" | cut -d \":\" -f2").read()[1:-1]
            if module == "":
                empty="none"
                lines.append(empty)
            else:
                lines.append(module)
    return lines   

# Function to read the time stamp of a file,
# and return the formatted date.
def getTimeStamp(path):
    stampData=t.localtime(os.stat(path).st_mtime)
    date=f"{stampData[0]}/{stampData[1]}/{stampData[2]}"
    return date

# Prints each line of a file by line,
# formatting each line with 4 space tabs.
def multilinePrint(list):
    for each in list:
        print(f'    {each}')

# Checks if there are available updates.
# Note: Compatible with Fedora, Oracle Linux, RedHat, CentOS, and Ubuntu;
# Add future compatibility here.
def checkAvailableUpdates():
    dist=os.popen("cat /etc/*-release | grep -i \"pretty\"").read()[13:-2].split()
    if str(dist[0]) == ("Fedora" or "Oracle" or "RedHat" or "CentOS"):
        updates=os.popen("yum updateinfo").read()[:-1].split('\n')[1:]
        if len(updates) != 0:
            return updates
        else:
            return "None"         
    elif dist[0] == "Ubuntu":
        updates=readFile("/var/lib/update-notifier/updates-available")[1:-1].split("\n")
        return updates
    else:
        return "N/A"

# Round up with configurable decimal place.
# Note: Created to display round up <1 GB when to show on TB scale.
# Pulled from https://realpython.com/python-rounding
def round_up(n, decimals=0):
    multiplier = 10 ** decimals
    return math.ceil(n * multiplier) / multiplier


# ------------------------------ #
#         CORE FUNCTIONS         #
# ------------------------------ #

# System Information
def infoSystem():
    hostname=s.getfqdn()
    uptime=os.popen('uptime -p').read()[:-1].split(' ', 1)[1]
    machineType=checkHypervisor()    
    # cpuName=os.popen('awk -F\':\' \'/^model name/ {print $2}\' /proc/cpuinfo | uniq | sed -e \'s/^[ \t]*//\'').read()[:-1]
    cpuName=cpuinfo.get_cpu_info()['brand']
    cpuArch=plat.processor()
    # This gets the number of Cores using lscpu's built in search function.
    cpuCores=os.popen('lscpu -b -p=Core,Socket | grep -v \'^#\' | sort -u | wc -l').read()[:-1]
    # os.cpu_count() gets the total number for threads on a system.
    cpuThreads=os.cpu_count()
    # The supported OSs all use a file in the /etc/ directory
    # that is delimited by "-release" and lists the "PRETTY_NAME"
    # of the OS.
    osRelease=os.popen("cat /etc/*-release | grep -i \"pretty\"").read()[13:-2]
    kernel=plat.release()
    activeUsers=os.popen('users').read()[:-1].split()
    sysIP=os.popen('hostname -I').read()[:-1].split()

    print(f'''
    {'='*30} System Information {'='*30}

    Hostname:                   {hostname}
    Uptime:                     {uptime}
    Machine Type:               {machineType}
    Processor Name:             {cpuName}
    CPU Arch:                   {cpuArch}
    CPU Cores:                  {cpuCores}
    CPU Threads:                {cpuThreads}
    Operating System:           {osRelease}
    Kernel:                     {kernel}''')
    for index, line in enumerate(activeUsers):
        if index == 0:
            print(f'    Active User(s):             {line}')
        else:
            print(f'                                {line}')
    for index, line in enumerate(sysIP):
        if index == 0:
            print(f'    IP Address(es):             {line}')
        else:
            print(f'                                {line}')

# CPU and Memory Usage
def usageCPUMem():
    memFree=psu.virtual_memory()[1]
    memTotal=psu.virtual_memory()[0]
    memAvail=f'{round_up(memFree/1024**3,1)} GB of {round_up(memTotal/1024**3,1)} GB'
    memUse=f'{psu.virtual_memory()[2]}% Used'
    swapUse=f'{psu.swap_memory()[3]}% Used'
    cpuUse=f'{psu.cpu_percent()}% Used'

    print(f'''
    {'='*31} CPU/Memory Usage {'='*31}
    
    Memory Free:                {memAvail}
    Memory Utilization:         {memUse}''')
    if None != psu.swap_memory()[3] != 0.0: # Hides swap unless it exists or usage is over 0. 
        print(f"    Swap Usage:                 {swapUse}")
    print(f"    CPU Usage:                  {cpuUse}")

# GPU Information
# Note: Runs slow, but may be able to convert to external libraries 
# in the future if requested.
def infoGPU():
    gpuID=os.popen("lspci | egrep -i \"Nvidia|Intel|AMD|ATI\" | grep VGA | cut -d \" \" -f1").read().split("\n")
    gpuInfo=os.popen("lspci | egrep -i \"Nvidia|Intel|AMD|ATI\" | grep VGA | awk -F: \'{print $3}\'").read()[:-1].split("\n")
    gpuMem=gpuMemory(gpuID)
    gpuDriver=gpuKernelDriver(gpuID)
    gpuKernel=gpuKernelMod(gpuID)

    print(f'''
    {'='*35} GPU/iGPU {'='*35}
    ''')
    # Information:                {gpuInfo}''')
    for index, line in enumerate(gpuInfo):
        if index == 0:
            print(f'    Info:                      {line}')
        else:
            print(f'                               {line}')
    for index, line in enumerate(gpuMem):
        if index == 0:
            print(f'    Memory:             {line}')
        else:
            print(f'                        {line}')
    for index, line in enumerate(gpuDriver):
        if index == 0:
            print(f'    Driver in Use:              {line}')
        else:
            print(f'                                {line}')
    for index, line in enumerate(gpuKernel):
        if index == 0:
            print(f'    Kernel:                     {line}')
        else:
            print(f'                                {line}')

# MyriadX Information
def infoMyriad():
    myriadInfo=os.popen("lsusb | grep -o \"Movidius MyriadX\"").read()[:-1]
    myriadCount=os.popen("lsusb | grep -o \"Movidius MyriadX\" | wc -l").read()[:-1]
    
    print(f'''
    {'='*36} Myriad {'='*36}
    
    Info:                       {myriadInfo}
    Count:                      {myriadCount}''')

# Disk Information for /home
# Note: Data is in bytes. Divided by 1024^3 to get disk use in Gigabytes.
# Note: Linux reserves some storage for the system (/boot, /swap, etc.),
# so Use + Free != Total in most cases.
def infoDisk():
    diskTotal=psu.disk_usage("/home")[0]/1024.0**3
    diskUse=psu.disk_usage("/home")[1]/1024.0**3
    diskFree=psu.disk_usage("/home")[2]/1024.0**3
    if diskTotal >= 1024.0: # If Total disk size is over 1024 GB, convert measurements to TB.
        diskTotal=f"{round_up(diskTotal/1024.0, 2)} TB"
        diskUse=f"{round_up(diskUse/1024.0, 3)} TB"
        diskFree=f"{round_up(diskFree/1024.0, 3)} TB"
    else:
        diskTotal=f"{round(diskTotal, 1)} GB" 
        diskUse=f"{round(diskUse, 1)} GB"
        diskFree=f"{round(diskFree, 1)} GB"

    diskPercent='{:.1f}%'.format(psu.disk_usage("/home")[3])

    print(f'''
    {'='*31} /home Disk Usage {'='*31}

    Total:                      {diskTotal}
    Used:                       {diskUse}
    Free:                       {diskFree}
    Percentage:                 {diskPercent}''')

# Asset Information
# Contents and the timestamp of /home/product_serial 
# to see when sdp_setup.sh was last run is printed.
# Copy product_serial from /sys/class/dmi/id/product_serial
# cp /sys/class/dmi/id/product_serial /home/product_serial ; chmod 444 /home/product_serial
def infoAsset():
    if os.path.exists("/var/run/reboot-required"):
        isRebootRequired="Yes"
    else:
        isRebootRequired="No"

    print(f'''
    {'='*29} Asset Administration {'='*29}

    Reboot Required:            {isRebootRequired}''')

# Available Updates Information.
# Note: Runs slower on RedHat-based distros, since a command is run on each load of the script.
#       Ubuntu prints lines from a file that is changed when updates are available. 
def infoUpdates():
    available=checkAvailableUpdates()

    print(f'''
    {'='*32} Avail. Updates {'='*32}
    ''')
    if available != "None":
        multilinePrint(available)
    else:
        print(f"    {available}")

# Prints out footer.
def infoFooter():
    print(f'''    
    {'='*80}
    ''')

# Main Function
# Call each info function here.
def main():
    infoSystem()
    usageCPUMem()
    infoGPU()
    # Prints Myriad section only if one is present on the system.
    if os.popen("lsusb | grep -o \"Movidius MyriadX\"").read()[:-1] != '':
        infoMyriad()
    # Prints Disk Usage only when True is returned by diskUsageHigh() function.
    # Note: Read Note on diskUsageHigh() function to change threshold.
    if diskUsageHigh() == True:
        infoDisk()
    infoAsset()
    infoUpdates()
    infoFooter()

# ---------------------------------- #
#         MAIN FUNCTION CALL         #
# ---------------------------------- #
main()
