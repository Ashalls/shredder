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

Use the arrow keys to navigate between the different options, and press enter
to select. When selecting drives, use enter to mark drives and y to select
marked drive(s).
"""

import enquiries
import subprocess
import os
import tempfile


def clear():
    """Clear the terminal"""
    os.system("clear")


def show_menu():
    """Display menu to user and let them choose what to do with their drive(s)"""
    clear()

    # Print title
    print("Shredder V1.5\n")

    # Print different options that the user can select between
    options = ['1 - Shred and check drive(s) for badblocks',
               '2 - Shred drive(s)',
               '3 - Check drive(s) for badblocks',
               "4 - Show serial ID's",
               "5 - Quit"]
    # Take input from user
    choice = enquiries.choose("Choose an option: ", options)

    # Check which option the user chose and run it

    if choice[0] == "1":            # Shred drive(s) and check for badblocks
        drives = select_drives()    # Run select_drive to let the user select drive(s) to perform the action on
        shred(drives)               # Run shred on selected drive(s)
        badblocks(drives)           # Run badblocks on selected drive(s)

    elif choice[0] == "2":          # Shred drive(s) only
        drives = select_drives()    # Run select_drive to let the user select drive(s) to perform the action on
        shred(drives)               # Run shred on selected drive(s)

    elif choice[0] == "3":          # Run badblocks on drive(s) only
        drives = select_drives()    # Run select_drive to let the user select drive(s) to perform the action on
        badblocks(drives)           # Run badblocks on selected drive(s)

    elif choice[0] == "4":          # Print serial id's so you can identify the drive(s)
        print_serial()              # Run print_serial which prints out the serial id's of each drive on screen

    elif choice[0] == "5":          # Exit the program
        clear()
        exit(-1)


def badblocks(drives):
    """
    Runs badblocks on selected drive(s) and creates temporary log files.
    Once badblocks has finished on all of the selected drive(s), it will
    copy those log files to the path stored in 'home' and rename them to
    the name of the selected drive(s). Ex. sda-badblocks.log
    """

    # Path to where the logfiles are stored
    home = "/home/shredder/projects/shred/log-files"

    # Clear the command line
    clear()

    print("Checking drives for badblocks...")

    processes = []
    for drive in drives:
        file = tempfile.NamedTemporaryFile(prefix='tempfile', dir='/tmp', delete=False)
        process = subprocess.Popen("badblocks -nv /dev/{} 2>&1".format(drive), shell=True, stdout=file)
        processes.append((process, file, drive))

    for process, file, drive in processes:
        logfile = open("{}/badblocks-{}.log".format(home, drive), "wb")
        process.wait()
        file.seek(0)
        logfile.write(file.read())
        file.close()


def shred(drives):
    """
    Runs shred on selected drive(s) and creates temporary log files.
    Once shred has finished on all of the selected drive(s), it will
    copy those log files to the path stored in 'home' and rename them to
    the name of the selected drive(s). Ex. sda-shred.log
    """

    # Path to where the logfiles are stored
    home = "/home/shredder/projects/shred/log-files"
    # Clears the command line
    clear()

    print("Shredding drives...")

    processes = []

    # Start shred command on selected drive(s)
    # Create a temporary log file with the name of the selected drive(s)
    for drive in drives:
        file = tempfile.NamedTemporaryFile(prefix='tempfile', dir='/tmp', delete=False)
        process = subprocess.Popen("shred -n 10 -z -v /dev/{} 2>&1".format(drive), shell=True, stdout=file)
        processes.append((process, file, drive))

    for process, file, drive in processes:
        logfile = open("{}/shred-{}.log".format(home, drive), "wb")
        process.wait()
        file.seek(0)
        logfile.write(file.read())
        file.close()
        logfile.close()


def select_drives():
    """Prints out all the drives on the system and uses fzf to select the drives."""

    # Clear the terminal
    clear()

    # Selected drives are stored here
    drives = []

    raw_drives = subprocess.Popen(["lsblk -no name,size,mountpoint | fzf -m --bind=enter:toggle+down,y:accept"
                                   " --layout=reverse --no-info --phony --header='ENTER to select | Y to accept'"
                                   " | cut -d' ' -f1"], stdout=subprocess.PIPE, shell=True)
    (out, err) = raw_drives.communicate()

    # Let the user now which drive(s) are selected
    print("You selected:")

    # Loop through the selected drives, decode them, split them onto a new line and print them on screen
    for line in out.decode("utf-8").split('\n'):
        drives.append(line)
        print(line)

    # Ask the user for confirmation
    confirmation = input("\nAre you sure you want to continue? The process will start immediately. Y/n: ").lower()

    # Check user confirmation
    if confirmation == 'n':
        clear()
        print("Goodbye.")
        exit(-1)

    # Return the drives so that it can be used by the other functions
    return drives[0:-1]


def print_serial():
    """
    Print the drivers serial id' so that it can be used
    to identify the drive(s). Ex. if a drive is bad, you
    can look for the serial number on the drive(s) so that
    you know which drive(s) that are bad.
    """

    # Clear the console
    clear()

    # Print the name and serial id' of the drive(s) connected to the system
    os.system("lsblk --nodeps -o name,serial")


def main():
    """Run the program from here."""
    
    show_menu()


if __name__ == '__main__':
    main()
