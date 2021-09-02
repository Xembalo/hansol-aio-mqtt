#!/bin/bash

#start script every minute

#modify ip of your hansol device and maybe port
deviceip="192.168.1.25:21710"

#mysql/mariadb credentials, on foreign host modify command at end of file
mysql_user="qhome"
mysql_pass="qhome"
mysql_scheme="qhome"


#function for calculation
calc() { awk "BEGIN{print $*}"; }

 #check month and start and end time
 year=$(date +%y)
 month=$(date +%m)
 day=$(date +%d)
 hour=$(date +%H)
 min=$(date +%M)
 now=20$year-$month-$day" "$hour:$min


bat1="0.00"
bat2="0.00"
pv1="0.00"
pv2="0.00"
demand1="0.0"
demand2="0.0"
feedin1="0.0"
feedin2="0.0"
load1="0.0"
load2="0.0"
temp1="0.0"
temp2="0.0"

demand="0.00"
feedin="0.00"
grid="0.0"
battery="0.0"
battery_soc="0.0"
temp="0.0"

Entries=$(wget -O - --quiet $deviceip/f0)
#1.seperation


str=$Entries
delimiter='</table>'
s=$str$delimiter
array=();
while [[ $s ]]; do
    array+=( "${s%%"$delimiter"*}" );
    s=${s#*"$delimiter"};
done;

#2.seperation

str=${array[0]}
delimiter='BT_SOC</td><td>'
s=$str$delimiter
array1=();
while [[ $s ]]; do
    array1+=( "${s%%"$delimiter"*}" );
    s=${s#*"$delimiter"};
done;

#3.seperation

str=${array1[1]}
delimiter='</td><td>'
s=$str$delimiter
array11=();
while [[ $s ]]; do
    #echo "${s%%"$delimiter"*}";
    array11+=( "${s%%"$delimiter"*}" );
    s=${s#*"$delimiter"};
done;


bat1=${array11[0]} #battery
pv1=${array11[6]} #pv
grid1=${array11[3]} #Grid
temp1=${array11[9]} #Temp


if (( $(awk 'BEGIN {print ("'$grid1'" >= "0.0")}') )); then
    demand1=$grid1
else 
    feedin1=$(calc $grid1*-1)
fi

#4.seperation

str=${array11[5]}
delimiter='</td></tr>'
s=$str$delimiter
array112=();
while [[ $s ]]; do
    array112+=( "${s%%"$delimiter"*}" );
    s=${s#*"$delimiter"};
done;

load1=${array112[0]} #Load



str=${array[7]}
delimiter='DATE</td><td'
s=$str$delimiter
array2=();
while [[ $s ]]; do
    array2+=( "${s%%"$delimiter"*}" );
    s=${s#*"$delimiter"};
done;

sleep 31
#second time after 31 seconds

Entries=$(wget -O - --quiet $deviceip/f0)
#1.seperation



str=$Entries
delimiter='</table>'
s=$str$delimiter
array=();
while [[ $s ]]; do
    array+=( "${s%%"$delimiter"*}" );
    s=${s#*"$delimiter"};
done;

#2.seperation

str=${array[0]}
delimiter='BT_SOC</td><td>'
s=$str$delimiter
array1=();
while [[ $s ]]; do
    array1+=( "${s%%"$delimiter"*}" );
    s=${s#*"$delimiter"};
done;

#3.seperation

str=${array1[1]}
delimiter='</td><td>'
s=$str$delimiter
array11=();
while [[ $s ]]; do
    array11+=( "${s%%"$delimiter"*}" );
    s=${s#*"$delimiter"};
done;


bat2=${array11[0]} #battery
pv2=${array11[6]} #pv
grid2=${array11[3]} #Grid
temp2=${array11[9]} #Temp

if (( $(awk 'BEGIN {print ("'$grid1'" >= "0.0")}') )); then
    demand2=$grid1
else 
    feedin2=$(calc $grid1*-1)
fi

#4.seperation

str=${array11[5]}
delimiter='</td></tr>'
s=$str$delimiter
array112=();
while [[ $s ]]; do
    array112+=( "${s%%"$delimiter"*}" );
    s=${s#*"$delimiter"};
done;

load2=${array112[0]} #Load



pv=$(calc $pv1+$pv2)
pv=$(calc $pv/2000)
bat=$(calc $bat1+$bat2)
bat=$(calc $bat/2)
demand=$(calc $demand1+$demand2)
demand=$(calc $demand/2000)
feedin=$(calc $feedin1+$feedin2)
feedin=$(calc $feedin/2000)
load=$(calc $load1+$load2)
load=$(calc $load/2000)
temp=$(calc $temp1+$temp2)
temp=$(calc $temp/2)

/usr/local/mariadb10/bin/mysql --user=$mysql_user --password=$mysql_pass $mysql_scheme << EOF
INSERT INTO \`logs\` (\`date\`, \`demand\`, \`feedin\`, \`consumption\`, \`battery_percent\`, \`pv\`, \`temperature\`) VALUES ('$now', '$demand', '$feedin', '$load', '$bat', '$pv', '$temp');
EOF
