#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to securely wipe hard drives.

This script uses shred to wipe multiple hard drives at once, over the course
of 10 passes, with the last pass setting every bit to 0.
After all the drives are finished wiping, badblocks is run on them, to see if
any of the drives have any, well, bad blocks.
Both the shredding and the checking for bad blocks is logged to a respective
log file per drive.
"""

import enquiries
import subprocess
import os
import tempfile


def clear():
    """Clear the terminal."""
    os.system("clear")

def show_menu():
    """Display menu to user."""
    clear()
    options = ['1 - Shred and check drive(s) for badblocks', '2 - Shred drive(s)', '3 - Check drive(s) for badblocks', "4 - Show serial ID's", "5 - Quit"]
    choice = enquiries.choose("Choose an option: ", options)

    if choice[0] == "1":
        drives = select_drives()
        shred(drives)
        badblocks(drives)
    elif choice[0] == "2":
        drives = select_drives()
        shred(drives)
    elif choice[0] == "3":
        drives = select_drives()
        badblocks(drives)
    elif choice[0] == "4":
        print_serial()
    elif choice[0] == "5":
        exit(-1)
    



def badblocks(drives):
    """Run the badblocks command with selected drives."""
    home = "/home/shredder/projects/shred/log-files"
    clear()
    print("Checking drives for badblocks...")

    processes = []
    for drive in drives:
        fil = tempfile.NamedTemporaryFile(prefix='tempfile', dir='/tmp', delete=False)
        process = subprocess.Popen("badblocks -nv /dev/{} 2>&1".format(drive), shell=True, stdout=fil)
        processes.append((process, fil, drive))

    for process, fil, drive in processes:
        logfile = open("{}/badblocks-{}.log".format(home, drive), "wb")
        process.wait()
        fil.seek(0)
        logfile.write(fil.read())
        fil.close()


def shred(drives):
    """Run the shred command with selected drives."""
    home = "/home/shredder/projects/shred/log-files"

    processes = []

    clear()
    print("Shredding drives...")

    for drive in drives:
        fil = tempfile.NamedTemporaryFile(prefix='tempfile', dir='/tmp', delete=False)
        process = subprocess.Popen("shred -n 10 -z -v /dev/{} 2>&1".format(drive), shell=True, stdout=fil)
        processes.append((process, fil, drive))

    for process, fil, drive in processes:
        logfile = open("{}/shred-{}.log".format(home, drive), "wb")
        process.wait()
        fil.seek(0)
        logfile.write(fil.read())
        fil.close()
        logfile.close()


def select_drives():
    """Let the user select the drives."""
    clear()
    drives = []

    raw_drives = subprocess.Popen(["lsblk -no name,size,mountpoint | fzf -m --bind=enter:toggle+down,y:accept --layout=reverse --no-info --phony --header='ENTER to select | Y to accept' | cut -d' ' -f1"], stdout=subprocess.PIPE, shell=True)
    (out, err) = raw_drives.communicate()

    print("You selected:")

    for line in out.decode("utf-8").split('\n'):
        drives.append(line)
        print(line)

    confirmation = input("\nAre you sure you want to continue? The process will start immediately. Y/n: ").lower()

    if confirmation == 'n':
        clear()
        print("Goodbye.")
        exit(-1)

    return drives[0:-1]



def print_serial():
    """Print the drives' serial numbers."""
    clear()
    os.system("lsblk --nodeps -o name,serial")


def main():
    """Run the program from here."""
    
    # Asks user what they want to do

    show_menu()


if __name__ == '__main__':
    main()
