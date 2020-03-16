#!/bin/sh

ps -ef |grep "facebook_login" | grep -v grep >.tmp
while read LINE
do
    PROCESS_ID=`echo -n ${LINE} |awk 'BEGIN {FS=" "} {print $2}'`
    echo $PROCESS_ID
    kill -9 $PROCESS_ID

done < .tmp
rm .tmp