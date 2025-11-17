import os
import sys
import signal
import time

SERVER_FIFO = "db_server.fifo"
DB = {
    1: "Nowak",
    2: "Kowalski",
    3: "Wisniewski",
    4: "Zielinski",
    5: "Lewandowski",
}

running = True

# --- Obsługa sygnałów ---
def stop_server(signum, frame):
    print("\nOtrzymano SIGUSR1, zamykanie serwera...")
    global running
    running = False

signal.signal(signal.SIGHUP, signal.SIG_IGN)   # Ignoruj SIGHUP
signal.signal(signal.SIGTERM, signal.SIG_IGN)  # Ignoruj SIGTERM
signal.signal(signal.SIGUSR1, stop_server)     # SIGUSR1 kończy serwer

# --- Główna funkcja serwera ---
def run_server():
    global running
    
    # Utwórz FIFO serwera
    if not os.path.exists(SERVER_FIFO):
        os.mkfifo(SERVER_FIFO)

    print(f"Serwer uruchomiony. PID: {os.getpid()}")
    print(f"Aby zakończyć: kill -USR1 {os.getpid()}")

    while running:
        print("\nCzekam na klienta...")
        
        # Otwórz FIFO (blokuje aż klient wyśle dane)
        with open(SERVER_FIFO, "r") as fifo:
            request = fifo.read().strip()

        if not request:
            continue

        print(f"Otrzymano: {request}")
        
        # Opóźnienie dla testowania wielu klientów
        print("Przetwarzam (5 sek)...")
        time.sleep(5)

        # Parsuj żądanie "PID:ID"
        try:
            pid_str, id_str = request.split(":")
            client_pid = int(pid_str)
            query_id = int(id_str)

            # Znajdź w bazie
            response = DB.get(query_id, "Nie ma")

            # Wyślij odpowiedź (pojedyncze os.write = niepodzielność)
            client_fifo = f"client_fifo_{client_pid}"
            if os.path.exists(client_fifo):
                fd = os.open(client_fifo, os.O_WRONLY)
                os.write(fd, response.encode('utf-8'))  # Pojedynczy zapis
                os.close(fd)
                print(f"Wysłano: {response}")

        except (ValueError, OSError) as e:
            print(f"Błąd: {e}")

    # Sprzątanie
    if os.path.exists(SERVER_FIFO):
        os.unlink(SERVER_FIFO)
    print("Serwer zakończony.")

if __name__ == "__main__":
    run_server()