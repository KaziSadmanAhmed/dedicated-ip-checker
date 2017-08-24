# Imports
import requests
import threading
import socket
import subprocess
import sys
import colorama
import shutil
import os

# Get the local IP using socket
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(3)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except socket.timeout:
        print(colorama.Fore.RED + "Error: Connection timeout when trying to get local IP")
        print(colorama.Fore.WHITE)
        input("Press Enter to exit.")
        sys.exit()

# Get the public IP using ipify api
def get_public_ip():
    try:
        return requests.get("https://api.ipify.org").text
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
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(3)
    host = "0.0.0.0"
    s.bind((host,port))
    s.listen(1)
    print(colorama.Fore.WHITE + "Server started successfully!")
    try:
        c, addr = s.accept()
        c.shutdown(socket.SHUT_RDWR)
        c.close()
    except socket.timeout:
        return

# Get random proxy from gimmeproxy
def random_proxy():
    try:
        r = requests.get("https://gimmeproxy.com/api/getProxy?protocol=http").json()
        ip, port = r["ip"], int(r["port"])
        return ip, port
    except:
        print(colorama.Fore.RED + "Error: Could not get a proxy!")
        print(colorama.Fore.WHITE)
        input("Press Enter to exit.")
        sys.exit()

# Create the client and connect to the server
def client(host, port):
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3)
            print(colorama.Fore.WHITE + "Client started successfully!")
            print(colorama.Fore.WHITE + "Getting a random proxy...")
            proxy_host, proxy_port = random_proxy()
            s.connect((proxy_host, proxy_port))
            print(colorama.Fore.GREEN + "Success!")
            break
        except socket.timeout:
            s.close()
            print(colorama.Fore.RED + "Error: Proxy down")
            print(colorama.Fore.RED + "Error: Restarting client...")

    global connection_status
    try:
        s.send("""GET http://{0}:{1} HTTP/1.1
                Host: http://{0}:{1} \r\n\r\n""".format(host, port).encode("utf-8"))
        r = s.recv(3000)
        print(colorama.Fore.GREEN + "Connected to server successfully!")
        connection_status = True
        s.close()
    except socket.timeout:
        print(colorama.Fore.RED + "Error: Client timed out")
        connection_status = False

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

    if len(sys.argv) > 1 and sys.argv[1] == "-p":
            test_port = int(sys.argv[2])
    else:
        test_port = 8000

    print(colorama.Fore.WHITE + "Using port", test_port)

    print(colorama.Fore.WHITE + "Getting local IP...")
    local_ip = get_local_ip()
    print(colorama.Fore.GREEN + "Success!")
    print(colorama.Fore.WHITE + "Local IP:", local_ip)

    print(colorama.Fore.WHITE + "Getting public IP...")
    public_ip = get_public_ip()
    print(colorama.Fore.GREEN + "Success!")
    print(colorama.Fore.WHITE + "Public IP:", public_ip)

    if local_ip != public_ip:
        print(colorama.Fore.MAGENTA + "Your computer appears to be behind a router!")
        print(colorama.Fore.WHITE + "Mapping port...")
        map_port(local_ip, test_port)
        print(colorama.Fore.GREEN + "Success!")

    print(colorama.Fore.WHITE + "Starting up server...")
    threading.Thread(target=server, args=[test_port]).start()

    print(colorama.Fore.WHITE + "Starting up client...")
    client(public_ip, test_port)

    if connection_status:
        print(colorama.Fore.GREEN + "\nYou have a dedicated IP address")
    else:
        print(colorama.Fore.RED + "\nYou have a shared IP address")

    print(colorama.Fore.WHITE)
    input("Press Enter to exit.")
    sys.exit()

# Run
if __name__ == "__main__":
    main()
