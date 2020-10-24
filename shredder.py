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
# Checks if enquiries is installed which is necessary for this program to work.
try:
    import enquiries
except ImportError as e:
    print("Enquiries is required for this program. Install it with 'pip3 install enquiries'.")
    exit(-1)

from pathlib import Path
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
    print("Shredder V1.7\n")

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
        # Run select_drive to let the user select drive(s) to perform the
        # action on
        drives = select_drives()
        shred(drives)               # Run shred on selected drive(s)
        badblocks(drives)           # Run badblocks on selected drive(s)

    elif choice[0] == "2":          # Shred drive(s) only
        # Run select_drive to let the user select drive(s) to perform the
        # action on
        drives = select_drives()
        shred(drives)               # Run shred on selected drive(s)

    elif choice[0] == "3":          # Run badblocks on drive(s) only
        # Run select_drive to let the user select drive(s) to perform the
        # action on
        drives = select_drives()
        badblocks(drives)           # Run badblocks on selected drive(s)

    # Print serial id's so you can identify the drive(s)
    elif choice[0] == "4":
        # Run print_serial which prints out the serial id's of each drive on
        # screen
        print_serial()

    elif choice[0] == "5":          # Exit the program
        clear()
        exit(-1)


def badblocks(drives):
    """
    Run badblocks on selected drive(s) and create a temporary log file for each drive.
    Once badblocks has finished on all of the selected drive(s), copy those log files
    to the path stored in 'home' and rename them to the name of the selected drive(s).
    """

    # Path to where the logfiles are stored
    home = "/home/shredder/projects/shred/log-files"

    # Clear the command line
    clear()

    print("Checking drives for badblocks...")

    processes = []
    for drive in drives:
        file = tempfile.NamedTemporaryFile(
            prefix='tempfile', dir='/tmp', delete=False)
        process = subprocess.Popen(
            "badblocks -nv /dev/{} 2>&1".format(drive),
            shell=True,
            stdout=file)
        processes.append((process, file, drive))

    for process, file, drive in processes:
        logfile = open("{}/badblocks-{}.log".format(home, drive), "wb")
        process.wait()
        file.seek(0)
        logfile.write(file.read())
        file.close()


def shred(drives):
    """
    Run shred on selected drive(s) and create a temporary log file for each drive.
    Once shred has finished on all of the selected drive(s), copy those log files
    to the path stored in 'home' and rename them to the name of the selected drive(s).
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
        file = tempfile.NamedTemporaryFile(
            prefix='tempfile', dir='/tmp', delete=False)
        process = subprocess.Popen(
            "shred -n 10 -z -v /dev/{} 2>&1".format(drive),
            shell=True,
            stdout=file)
        processes.append((process, file, drive))

    for process, file, drive in processes:
        logfile = open("{}/shred-{}.log".format(home, drive), "wb")
        process.wait()
        file.seek(0)
        logfile.write(file.read())
        file.close()
        logfile.close()


def select_drives():
    """Print out all the drives on the system and use fzf to let the user select the drives."""

    # Clear the terminal
    clear()

    # Selected drives are stored here
    drives = []

    raw_drives = subprocess.Popen(
        [
            "lsblk -no name,size,mountpoint | fzf -m --bind=enter:toggle+down,y:accept"
            " --layout=reverse --no-info --phony --header='ENTER to select | Y to accept'"
            " | cut -d' ' -f1"],
        stdout=subprocess.PIPE,
        shell=True)
    (out, err) = raw_drives.communicate()

    # Let the user now which drive(s) are selected
    print("You selected:")

    # Loop through the selected drives, decode them, split them onto a new
    # line and print them on screen
    for line in out.decode("utf-8").split('\n'):
        drives.append(line)
        print(line)

    # Ask the user for confirmation
    confirmation = input(
        "\nAre you sure you want to continue? The process will start immediately. Y/n: ").lower()

    # Check user confirmation
    if confirmation == 'n':
        clear()
        print("Goodbye.")
        exit(-1)

    # Return the drives so that it can be used by the other functions
    return drives[0:-1]


def print_serial():
    """Print the drivers serial id' so that it can be used to identify the drive(s)."""

    # Clear the console
    clear()

    # Print the name and serial id' of the drive(s) connected to the system
    os.system("lsblk --nodeps -o name,serial")


def main():
    """Run the program from here."""
    fzf_location = Path("/usr/bin/fzf")

    # Checks if fzf is installed
    if fzf_location.is_file():
        pass
    else:
        print(
            "Fzf is required for this program. Install it with 'sudo apt-get install fzf'.")
        exit(-1)

    show_menu()


if __name__ == '__main__':
    main()
