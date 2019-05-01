# Pi-Hunter

**Pi-Hunter** is a tool made to scan a range of ip addresses looking for raspberry pi's with default SSH credencials.

## Getting Started
Pretty straight forward installation, clone the repository and install the requirements.
```
git clone https://github.com/Anet369/Pi-Hunter.git
cd Pi-Hunter
sudo pip install -r requirements.txt
```
and you should be ready to go.

One line version:
```
git clone https://github.com/Anet369/Pi-Hunter.git && cd Pi-Hunter && sudo pip install -r requirements.txt
```
## Requirements
**Pi-Hunter** is using a couple of python modules
* **paramiko**
* **subprocess**
* **threading**
* **socket**
* **ipcalc**
* **nmap** 
* **netifaces**
* **netaddr**

All the requirements is listed in [requirements.txt](requirements.txt)


## Credit
This project is inspired by the awesome tool **rpi-hunter** made by **[BusesCanFly](https://github.com/BusesCanFly/rpi-hunter)**

## Usage
For scanning your local network and executing a **whoami** command
```
./pi-hunter.py -l -c whoami
```
Scanning an ip range and executing **whoami**
```
./pi-hunter.py -r 192.168.0.0/24 -c whoami
```
And last you can use a ip-list in the form of a file
```
./pi-hunter.py -f filename -c whoami
```

## Todo
* **Add a show only successful results option**
* **Add a function to verify that the device is a raspberry pi and not just a regular ssh enabled device**


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) for more information


# *Disclamer*
## Please use with responsibility, Pi-Hunter is made for fun and other legal whitehat purposes, please do not use without permission from the owner.
## I am in no way liable or have any responiblity whatsoever for what you use this tool for.
