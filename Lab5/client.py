import sysv_ipc
import os
import time
import sys

# Keys for the queues
KEY_INPUT = 12345
KEY_OUTPUT = 54321

def main():
    try:
        mq_input = sysv_ipc.MessageQueue(KEY_INPUT)
        mq_output = sysv_ipc.MessageQueue(KEY_OUTPUT)
    except sysv_ipc.ExistentialError:
        print("Queues do not exist. Is the server running?")
        sys.exit(1)

    pid = os.getpid()
    print(f"Client PID: {pid}")
    if len(sys.argv) > 1 and sys.argv[1] == "stop":
        print("Sending stop command...")
        # Send stop message with type 1 (or any type, server checks content)
        mq_input.send("stop", type=pid)
        print("Stop command sent.")
        return

    
    country = input("Podaj nazwę kraju: ")

    

    # Send all requests first
    for i in range(10):
        print(f"Sending request: {country}")
        mq_input.send(country, type=pid)
        time.sleep(1) # 1 second delay between requests as requested

    print("All requests sent. Waiting for responses...")

    # Receive all responses
    for _ in range(10):
        try:
            # Receive message with type = pid
            message_bytes, _ = mq_output.receive(type=pid)
            response = message_bytes.decode()
            print(f"Received response: {response}")
        except sysv_ipc.BusyError:
            pass

    print("Client finished.")

if __name__ == "__main__":
    main()
