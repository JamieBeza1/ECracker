char_list = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u",
               "v", "w", "x", "y", "z"]
clients = ['111.111.111.111', '222.222.222.222']


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
        ip = client[0]
        divisions[ip] = char_list[start:end]
        start = end
    return divisions

def print_divisions(divisions):
    for ip, chars in divisions.items():
        print(f"Client {ip}: {chars}")

divisions = divide_calcs()
print_divisions(divisions)