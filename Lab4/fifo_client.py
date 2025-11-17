import os
import sys

SERVER_FIFO = "db_server.fifo"

def run_client():
    # Sprawdź serwer
    if not os.path.exists(SERVER_FIFO):
        print("Błąd: Serwer nie działa.")
        sys.exit(1)

    # Pobierz ID
    query_id = input("Podaj ID: ").strip()
    if not query_id.isdigit():
        print("ID musi być liczbą.")
        sys.exit(1)

    # Utwórz FIFO klienta
    client_pid = os.getpid()
    client_fifo = f"client_fifo_{client_pid}"
    if not os.path.exists(client_fifo):
        os.mkfifo(client_fifo)

    try:
        # Wyślij żądanie (pojedyncze os.write = niepodzielność)
        request = f"{client_pid}:{query_id}"
        fd = os.open(SERVER_FIFO, os.O_WRONLY)
        os.write(fd, request.encode('utf-8'))  # Pojedynczy zapis
        os.close(fd)

        print("Wysłano żądanie, czekam...")

        # Odbierz odpowiedź (blokująco)
        with open(client_fifo, "r") as fifo:
            response = fifo.read()

        print(f"Odpowiedź: {response}")

    except OSError as e:
        print(f"Błąd: {e}")

if __name__ == "__main__":
    run_client()