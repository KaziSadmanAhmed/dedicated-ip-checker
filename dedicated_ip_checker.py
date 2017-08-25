# Imports
import requests
from bs4 import BeautifulSoup as BS
import threading
import socket
import subprocess
import sys
import colorama
import shutil
import os
import random

# Get the local IP using socket
def get_local_ip():
    print(colorama.Fore.WHITE + "Getting local IP...")
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(3)
    try:
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        print(colorama.Fore.GREEN + "Success!")
        return local_ip
    except socket.timeout:
        print(colorama.Fore.RED + "Error: Connection timeout when trying to get local IP")
        print(colorama.Fore.WHITE)
        input("Press Enter to exit.")
        sys.exit()

# Get the public IP using ipify api
def get_public_ip():
    print(colorama.Fore.WHITE + "Getting public IP...")
    try:
        public_ip = requests.get("https://api.ipify.org").text
        print(colorama.Fore.GREEN + "Success!")
        return public_ip
    except:
        print(colorama.Fore.RED + "Error: Could not get public IP!")
        print(colorama.Fore.WHITE)
        input("Press Enter to exit.")
        sys.exit()

# Map specific port to specific IP using miniupnpc
def map_port(ip, port):
    try:
        subprocess.check_output(["upnpc/upnpc-static.exe", "-a", ip, str(port), str(port), "tcp", "10"], cwd="upnpc")
    except FileNotFoundError:
        print(colorama.Fore.RED + "Error: Could not find upnpc files!")
        print(colorama.Fore.WHITE)
        input("Press Enter to exit.")
        sys.exit()
    except NotADirectoryError:
        print(colorama.Fore.RED + "Error: Could not find upnpc files!")
        print(colorama.Fore.WHITE)
        input("Press Enter to exit.")
        sys.exit()
    except subprocess.CalledProcessError as e:
        print(colorama.Fore.RED + "Unexpected error when mapping port.", "Error:", e)
        print(colorama.Fore.WHITE)
        input("Press Enter to exit.")
        sys.exit()

# Create a TCP server using socket
def server(port):
    print(colorama.Fore.WHITE + "Starting up server...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = "0.0.0.0"
    s.bind((host,port))
    s.listen(1)
    print(colorama.Fore.WHITE + "Server started successfully!")
    c, addr = s.accept()
    c.shutdown(socket.SHUT_RDWR)
    c.close()

# Check the mapped port via canyouseeme.org
def check_port(ip, port, initial_selection=False):
    if not initial_selection:
        print("Checking port...")
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"}
    data = {"IP": ip, "port": port}

    try:
        r = requests.post("http://canyouseeme.org", headers=headers, data=data)
        if r.ok:
            soup = BS(r.text, "lxml")

            if soup.find("font", {"color": "green"}):
                return True
            else:
                return False

        else:
            raise Exception

    except Exception as e:
        print(e)
        print(colorama.Fore.RED + "Error: Could not check the port!")
        print(colorama.Fore.WHITE)
        input("Press Enter to exit.")
        sys.exit()

# Show welcome messages
def welcome():
    terminal_width = shutil.get_terminal_size().columns
    print(colorama.Style.BRIGHT + colorama.Fore.CYAN + "\n" + "Dedicated IP Checker".center(terminal_width))
    print(colorama.Fore.YELLOW + "Made by Kazi Sadman Ahmed".center(terminal_width))

# Supercontroller
def main():
    os.system("cls")
    colorama.init()

    welcome()

    print(colorama.Fore.MAGENTA + "\n>>> Make sure you have the firewall turned off <<<")

    print(colorama.Fore.WHITE + "\nStarting...")

    local_ip = get_local_ip()
    print(colorama.Fore.WHITE + "Local IP:", local_ip)

    public_ip = get_public_ip()
    print(colorama.Fore.WHITE + "Public IP:", public_ip)

    if len(sys.argv) > 1 and sys.argv[1] == "-p":
            test_port = int(sys.argv[2])
    else:
        while True:
            test_port = random.randrange(10000, 65536)
            if not check_port(public_ip, test_port, initial_selection=True): break

    print(colorama.Fore.WHITE + "Using port", test_port)

    if local_ip != public_ip:
        print(colorama.Fore.MAGENTA + "Your computer appears to be behind a router!")
        print(colorama.Fore.WHITE + "Mapping port...")
        map_port(local_ip, test_port)
        print(colorama.Fore.GREEN + "Success!")

    threading.Thread(target=server, args=[test_port]).start()

    result = check_port(public_ip, test_port)

    if result:
        print(colorama.Fore.GREEN + "\nYou have a dedicated IP address")
    else:
        print(colorama.Fore.RED + "\nYou have a shared IP address")

    print(colorama.Fore.WHITE)
    input("Press Enter to exit.")
    sys.exit()

# Run
if __name__ == "__main__":
    main()
