Efficient Cracker POC

1) Choose a password. it is recommended to just use a 4-5 char length password with all lower case chars. As this is just a POC to see how the workload can be distributed we dont want it to be running for too long. 
2) Apply MD5 hashing algorithm to the password and supply the hex string in the server script where the 'pword' global variable is initialised.
3) run the server - specify 'n' as we only want to use a-z chars for now (again this is to just cut down on the time complexities as this is just a POC)
4) Go to the client script and specify how manny clients you want to connect. This simulates the clients in a botnet.
5) run the client script
6) switch back to the server terminal and press enter to launch the cracker

This is just a POC to show how the workload of brute force can be distributed in a botnet. Unfortunately the more client threads you open by specify,
 the slower the alorgithm is as it all has to be run on your pc. In a real application, this wouldn't be the case as each client would be run on a unique pc.

