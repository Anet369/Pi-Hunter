# Pi-Hunter

**Pi-Hunter** is a tool made to scan a range of ip addresses looking for raspberry pi's with default SSH credencials.

## Getting Started
straight forward installation, Clone the repository, give some permissions and run the install.py with root privileges.
```
git clone https://github.com/Anet369/Pi-Hunter.git
cd Pi-Hunter
pip install -r requirements.txt
```
and you should be ready to go.

One line version:
```
git clone https://github.com/Anet369/Pi-Hunter.git && cd Pi-Hunter && pip install -r requirements.txt
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

## Todo
* **Add the function to verify that the device is a raspberry pi and not just a regular ssh enabled device**


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) for more information


# *Disclamer*
## Please use with responsibility, Pi-Hunter is made for fun and other legal whitehat purposes.
## I am in no way liable or have any responiblity for what you use with this tool for.
