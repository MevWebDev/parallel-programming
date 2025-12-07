import os
import sys

SERVER_FIFO = "db_server.fifo"

def run_client():
    if not os.path.exists(SERVER_FIFO):
        print("Błąd: Serwer nie działa.")
        sys.exit(1)

    query_id = input("Podaj ID: ").strip()
    if not query_id.isdigit():
        print("ID musi być liczbą.")
        sys.exit(1)

    client_pid = os.getpid()
    client_fifo = f"client_fifo_{client_pid}"
    
    if not os.path.exists(client_fifo):
        os.mkfifo(client_fifo)

    try:
        # Format zgodny z zadaniem: "ID:ścieżka_do_kolejki"
        request = f"{query_id}:{client_fifo}\n"
        
        # NIEPODZIELNE WYSŁANIE (os.write)
        fd = os.open(SERVER_FIFO, os.O_WRONLY)
        os.write(fd, request.encode('utf-8'))
        os.close(fd)

        print("Wysłano żądanie, czekam...")

        # Blokujący odczyt odpowiedzi
        with open(client_fifo, "r") as fifo:
            response = fifo.read()

        print(f"Odpowiedź: {response}")

    except OSError as e:
        print(f"Błąd: {e}")
    finally:
        # Opcjonalnie: zostaw dla prezentacji lub usuń
        # if os.path.exists(client_fifo):
        #     os.unlink(client_fifo)
        pass

if __name__ == "__main__":
    run_client()