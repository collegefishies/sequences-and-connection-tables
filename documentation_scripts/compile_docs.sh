#!/bin/bash
# pip install pdoc3

LABNAME=ybclock
WINUSER=YbClockReloaded
UNIXLOCATION=/mnt/c/Users/$WINUSER/labscript-suite/userlib/labscriptlib/$LABNAME
CODEPATH=$UNIXLOCATION

cd UNIXLOCATION
echo $UNIXLOCATION

function pause(){
 read -s -n 1 -p "Press any key to continue . . ."
 echo ""
}

pause
