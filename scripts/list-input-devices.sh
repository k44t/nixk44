#!/bin/sh
for d in /dev/input/event*; do
	echo $d: $(cat /sys/class/input/$(basename $d)/device/name)
done