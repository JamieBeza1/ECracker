import socket
import json
import itertools
import threading
import hashlib

host = '192.168.1.145'
port = 4444
length = None
max_length = 14
min_length = 1
pword = {}

termination_flag_lock = threading.Lock()
termination_flag = False
print_lock = threading.Lock()

def connect_client(client_id):
    global termination_flag, pword
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    msg = s.recv(2048)
    data_rcvd = json.loads(msg.decode('utf-8'))

    def attempt_combinations(start_char, length):
        global termination_flag, pword
        for combination in itertools.product(data_rcvd["char_list"], repeat=length - 1):
            with termination_flag_lock:
                if termination_flag:
                    return
            attempt = start_char + ''.join(combination)
            hash = hashlib.md5(str(attempt).encode()).hexdigest()
            with print_lock:
                print(f'Client {client_id}   |   Plaintext Attempt: {attempt}   |   MD5 Attempt: {hash}')
            if hash == data_rcvd["password"]:
                with print_lock:
                    print(f'Client {client_id} cracked the password: {attempt} from {hash}')
                pword["password"] = attempt
                s.sendall(json.dumps(pword).encode('utf-8'))
                with termination_flag_lock:
                    termination_flag = True
                return True
        return False

    def crack_unknown():
        for length in range(min_length, max_length + 1):
            for start_char in data_rcvd["starting_chars"]:
                if attempt_combinations(start_char, length):
                    return
        with print_lock:
            print(f'Client {client_id} did not find the password.')

    def listen_for_termination():
        global termination_flag
        while True:
            msg = s.recv(1024)
            data = json.loads(msg.decode('utf-8'))
            if data.get("is_finished"):
                with print_lock:
                    print(f'Client {client_id} received termination signal.')
                with termination_flag_lock:
                    termination_flag = True
                break

    crack_thread = threading.Thread(target=crack_unknown)
    crack_thread.start()

    termination_thread = threading.Thread(target=listen_for_termination)
    termination_thread.start()

    crack_thread.join()
    termination_thread.join()
    s.close()

def simulate_clients(num_clients):
    threads = []
    for i in range(num_clients):
        t = threading.Thread(target=connect_client, args=(i,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

if __name__ == "__main__":
    simulate_clients(30)


