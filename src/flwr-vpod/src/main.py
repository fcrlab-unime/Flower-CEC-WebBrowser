import multiprocessing as mp
import requests as r
import client_flower as cf
from time import sleep

PERIOD_ACTIVE_SESSIONS = 10  # Define this according to your requirements

def get_active_sessions():
    url = "http://flwr-cec-kleint-gateway:11355/getActiveSessions/client"
    response = r.get(url)
    return response.json()['sessions']


def main():
    processes = {}
    print("Starting main loop")
    while True:
        sleep(PERIOD_ACTIVE_SESSIONS)
        print("Checking active sessions")
        sessions = get_active_sessions()
        print("Active sessions: ", sessions)
        
        # Remove processes for sessions that are no longer active
        for session in list(processes.keys()):
            if session not in sessions:
                kill_client(processes[session])
                del processes[session]
        
        # Add processes for new active sessions
        for session in sessions:
            if session not in processes:
                processes[session] = add_client(session)
                
        print("Active processes: ", processes)  


def add_client(session):
    process = mp.Process(target=cf.new_client_flwr, args=(session,))
    process.start()
    return process


def kill_client(process):
    process.terminate()
    process.join()
    return


if __name__ == "__main__":
    main()
