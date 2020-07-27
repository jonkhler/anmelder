#!/bin/sh
to=$1
subject=$2
body=$3
from=$4
thunderbird -compose "subject='$subject',to='$to',body=$body,from=$from"
sleep 0.25
xdotool key CTRL+Return
sleep 0.25
xdotool key Return
