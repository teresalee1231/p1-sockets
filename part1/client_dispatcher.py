# Dispatches a given number of clients.
import client
import threading

NUM_CLIENTS = 4

def run_dispatcher():
    for i in range(NUM_CLIENTS):
        print(f'CREATE CLIENT {i}')
        # Run thread for client
        c_thread = threading.Thread(target = client.run_client, args = tuple())
        c_thread.start()

if __name__ == '__main__':
    run_dispatcher()