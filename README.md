What is Shredder?
-----------------
Shredder is a script to securely wipe hard drives.
This script uses shred to wipe multiple hard drives at once, over the course
of 10 passes, with the last pass setting every bit to 0.
After all the drives are finished wiping, badblocks is run on them, to see if
any of the drives have any, well, bad blocks.
Both the shredding and the checking for bad blocks is logged to a respective 
log file per drive.

-----------------
How to use:
-----------------

Use arrow keys to navigate between the different options.
Press ENTER to select.
When selecting drives, use ENTER to mark, and Y to select marked drives.
