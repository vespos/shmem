#!/bin/bash

source /reg/g/psdm/etc/psconda.sh -py3

if [ $(echo $HOSTNAME | grep -ic -e "psana" -e "drp-srcf") -eq 1 ]
then
    echo "Run on psana or ffb."
    mpirun python -u driver.py
elif [ $(echo $HOSTNAME | grep -ic -e "daq") -eq 1 ]
then
    echo "Run on mon node."
    `which mpirun` --oversubscribe -H daq-xpp-mon07,daq-xpp-mon08,daq-xpp-mon09 -n 24 python -u driver.py
else
    echo "Can't run on this host."
fi
