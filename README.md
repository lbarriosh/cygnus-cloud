
###Welcome to the CygnusCloud GitHub page!

CygnusCloud is developed as a master thesis project by Luis Barrios, Adrián Fernández and 
Samuel Guayerbas at the Complutense University of Madrid.

Our aim is turn every non-specialized computer room in the campus into a computer science lab. 
This will allow students to do almost every kind of assignments out the crowded computer science labs.

CygnusCloud also has more benefits as well:
* it saves money to the university. We can use cheaper (and less power-hungry) PCs on the computer rooms.
* it requires much less bureaucracy. Nowadays, if a teacher wants a specific software to be installed in a computer room, he or she will have to wait for a month. And if the software is not properly installed, they'll have to wait more. With CygnusCloud, teachers will be able to install and distribute custom virtual machines within a few hours.
* it runs perfectly on four-year-old servers. To deploy it, you'll just need a gigabit LAN and a bunch of servers.

###So... how does it work?

The CygnusCloud infrastructure has three kinds of machines:

* the virtual machine servers. They host qemu/KVM virtual machines.
* the cluster server. It balances the load between a set of virtual machine servers
* the web server. This machine hosts the website that allow the users to create and communicate with virtual machines. The website uses Web2Py and some JavaScript as well.

### What we have done so far
We released the 1.0+ version on March 2013. This is the first release, and allows users to
* create and destroy virtual machines
* manage the infrastructure (at a basic level)
* manage the user accounts
