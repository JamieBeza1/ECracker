import socket
import threading
import json
#import colored
import time
import hashlib

# Server Variables
host = '192.168.1.145'  # Change this to your actual server IP
port = 4444

# Global variables
clients = {}
clients_lock = threading.Lock()
print_lock = threading.Lock()
start_event = threading.Event()

# Char sets
chars_lower = list("abcdefghijklmnopqrstuvwxyz")
chars_upper = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
digits = list("0123456789")
special_chars = list("!£$%^&*,./?'#_-")
length = None

# Char list for brute forcing
char_list = []
divisions = {}
# Password
#pword = 'ab56b4d92b40713acc5af89985d4b786' # MD5 hash of 'abcde'
pword = 'fd3ff19636453e9bc8965e3316efdc1b' # MD5 hash of 'zabcd'
# Network strings
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

strt_time = None

# Calculates the chars in the brute force array
def calc_complexity():
    global length, char_list, pword
    char_list.clear()  # Clear the char_list to avoid duplications
    set_complexity = input("Do you want to specify the password complexity? (Y/N)").upper()
    if set_complexity == "N":
        char_list.extend(chars_lower)
        #manually sets pword
        length = 3
    if set_complexity == "Y":
        lower = input("Do you want to include LOWER case chars? (Y/N): ")
        upper = input("Do you want to include UPPER case chars? (Y/N): ")
        digs = input("Do you want to include DIGITS? (Y/N): ")
        spec = input("Do you want to include SPECIAL chars? (Y/N): ")
        size = input("Do you know the length of the password? (Y/N): ")
        if size.upper() == "Y":
            length = int(input("How many chars long is the password? "))
            if lower.upper() == "Y":
                char_list.extend(chars_lower)
            if upper.upper() == "Y":
                char_list.extend(chars_upper)
            if digs.upper() == "Y":
                char_list.extend(digits)
            if spec.upper() == "Y":
                char_list.extend(special_chars)
            permutations = (len(char_list)) ** length
            with print_lock:
                print("The password complexity has {} possible combinations".format(permutations))
        else:
            with print_lock:
                print("No length selected. The cracking tool will now run recursively. This may take a while...")
            if lower.upper() == "Y":
                char_list.extend(chars_lower)
            if upper.upper() == "Y":
                char_list.extend(chars_upper)
            if digs.upper() == "Y":
                char_list.extend(digits)
            if spec.upper() == "Y":
                char_list.extend(special_chars)

def handle_client(c, addr):
    with print_lock:
        print(f'Connection from {addr[0]}:{addr[-1]} has been established!')
    with clients_lock:
        clients[addr[0]+":"+str(addr[-1])] = [c, addr]
        with print_lock:
            print(f'There are {len(clients)} connected clients')
    start_event.wait()  # wait until server is ready to send data
    send_client_chars(c, addr[0], addr[-1])

def send_client_chars(c, client_ip, client_port):
    with clients_lock: # lock clients to stop new clients joining once launched
        divisions = divide_calcs()
    chars = divisions.get(client_ip+":"+str(client_port)) # gets chars for the client from the divisions object
    data = {"starting_chars": chars, "char_list": char_list, "length": length, "password": pword}
    c.sendall(json.dumps(data).encode('utf-8'))
    with print_lock:
        print(f'Data sent to {client_ip}:{client_port} with message: {data}')
    data_rcvd = c.recv(1024)
    cracked_password = json.loads(data_rcvd.decode('utf-8'))
    result = cracked_password["password"]
    hash = hashlib.md5(result.encode()).hexdigest()
    if hash == pword:
        end_time = time.time()
        text = '\033[36m' + cracked_password["password"] + '\033[0m'  # color formatting cyan then back to normal
        with print_lock:
            print(f'Password Cracked from {client_ip}: {text}')
            print(f'Time taken to crack the password: {end_time - strt_time} seconds')
        terminate_all_clients(c, client_ip)

def terminate_all_clients(c, client_ip):
    term = {"is_finished": True}
    c.sendall(json.dumps(term).encode('utf-8'))


def start_server():
    global strt_time
    s.bind((host, port))
    s.listen()
    with print_lock:
        print(f'\nSERVER OUTPUT\nServer listening @{host}:{port}')
    accept_thread = threading.Thread(target=accept_clients)
    accept_thread.start()
    input("Press Enter when ready to launch the cracker...\n")
    strt_time = time.time()
    start_event.set()  # Signal all client threads to proceed
    accept_thread.join()  # Wait for the accept thread to finish

def accept_clients():
    while True:
        c, addr = s.accept()
        client_thread = threading.Thread(target=handle_client, args=(c, addr))
        client_thread.start()

def divide_calcs():
    num_chars = len(char_list)
    num_clients = len(clients)
    step = num_chars // num_clients
    remainder = num_chars % num_clients
    divisions = {}
    start = 0
    for client in clients:
        end = start + step + (1 if remainder > 0 else 0)
        if remainder > 0:
            remainder -= 1
        if end > num_chars:
            end = num_chars
        ip = client
        divisions[ip] = char_list[start:end]
        start = end
    return divisions

def main():
    calc_complexity()
    start_server()

if __name__ == '__main__':
    main()
