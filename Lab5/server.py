import sysv_ipc
import time
import os
import signal
import sys

# Keys for the queues
KEY_INPUT = 12345
KEY_OUTPUT = 54321

# Geography dictionary
CAPITALS = {
    'Polska': 'Warszawa',
    'Francja': 'Paryż',
    'Niemcy': 'Berlin',
    'Hiszpania': 'Madryt',
    'Włochy': 'Rzym',
    'Wielka Brytania': 'Londyn',
    'Rosja': 'Moskwa',
    'Czechy': 'Praga',
    'Słowacja': 'Bratysława',
    'Ukraina': 'Kijów'
}

def main():
    print("Server starting...")
    
    # Create queues. IPC_CREAT ensures they are created if they don't exist.
    try:
        mq_input = sysv_ipc.MessageQueue(KEY_INPUT, sysv_ipc.IPC_CREAT)
        mq_output = sysv_ipc.MessageQueue(KEY_OUTPUT, sysv_ipc.IPC_CREAT)
    except sysv_ipc.ExistentialError:
        print("Error creating queues. They might already exist.")
        # Try to attach to existing ones just in case, or fail.
        mq_input = sysv_ipc.MessageQueue(KEY_INPUT)
        mq_output = sysv_ipc.MessageQueue(KEY_OUTPUT)

    print(f"Queues created/attached. Input Key: {KEY_INPUT}, Output Key: {KEY_OUTPUT}")
    print("Waiting for messages...")

    while True:
        try:
            # Receive message from input queue
            # receive returns a tuple (message, type)
            # message is bytes
            message_bytes, msg_type = mq_input.receive()
            message_str = message_bytes.decode().strip()
            
            print(f"Received request: '{message_str}' from PID {msg_type}")

            if message_str.lower() == "stop":
                print("Stop command received. Shutting down...")
                break

            # Process request
            response = CAPITALS.get(message_str, "Nie wiem")
            
            # Simulate processing time
            print("Processing...")
            time.sleep(2)
            
            # Send response to output queue with type = client's PID
            mq_output.send(response.encode(), type=msg_type)
            print(f"Sent response: '{response}' to PID {msg_type}")

        except sysv_ipc.BusyError:
            # Should not happen with blocking receive
            pass
        except KeyboardInterrupt:
            print("\nServer interrupted by user.")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            break

    # Cleanup
    print("Cleaning up queues...")
    try:
        mq_input.remove()
        mq_output.remove()
        print("Queues removed.")
    except Exception as e:
        print(f"Error removing queues: {e}")

if __name__ == "__main__":
    main()
