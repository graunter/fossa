#!/bin/bash

if [ ! -d /var/log/fossa ]; then
        mkdir /var/log/fossa
        echo "Folder for logs was created"
fi

/opt/fossa/fossa -v &>> /var/log/fossa/fossa.log & #> /dev/null 2>&1

echo $! > /var/run/fossa.pid
