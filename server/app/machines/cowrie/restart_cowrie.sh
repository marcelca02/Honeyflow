#!/bin/bash

# Reiniciar cowrie para que se aplique el  puerto 22
su - cowrie << EOF
    cd cowrie
    bin/cowrie stop
    bin/cowrie start
    exit
    
EOF 
exec /bin/bash

