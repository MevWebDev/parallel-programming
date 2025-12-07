import os
import sys
import signal
import time
import errno

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
    sys.exit(0)

signal.signal(signal.SIGHUP, signal.SIG_IGN)
signal.signal(signal.SIGTERM, signal.SIG_IGN)
signal.signal(signal.SIGUSR1, stop_server)

# --- Główna funkcja serwera ---
def run_server():
    
    
    if not os.path.exists(SERVER_FIFO):
        os.mkfifo(SERVER_FIFO)

    print(f"Serwer uruchomiony. PID: {os.getpid()}")
    print(f"Aby zakończyć: kill -USR1 {os.getpid()}")
    
    fifo = None
    fifo_write = -1
    
    try:
        print("\nCzekam na klientów...")
        # Otwórz do odczytu (blokuje, aż ktoś otworzy do zapisu)
        fifo = open(SERVER_FIFO, "r")
        
        # Otwórz do zapisu, żeby kolejka nie zamykała się po zakończeniu klienta
        fifo_write = os.open(SERVER_FIFO, os.O_WRONLY | os.O_NDELAY)
        
        while running:
            # Blokujący odczyt
            try:
                request = fifo.readline().strip()
            except OSError as e:
                if e.errno == errno.EINTR:  # Przerwane przez sygnał
                    
                    continue
                raise

            # Jeśli pusta linia, kontynuuj (ale nie zamykaj FIFO!)
            if not request:
                continue

            # Tutaj mamy prawdziwe żądanie
            print(f"\nOtrzymano: {request}")
            print("Przetwarzam (5 sek)...")
            time.sleep(5)

            try:
                # Format: "ID:ścieżka_do_fifo"
                id_str, client_fifo_path = request.split(":", 1)
                query_id = int(id_str)

                response = DB.get(query_id, "Nie ma")

                # NIEPODZIELNE WYSŁANIE (os.write)
                if os.path.exists(client_fifo_path):
                    fd = os.open(client_fifo_path, os.O_WRONLY)
                    os.write(fd, response.encode('utf-8'))
                    os.close(fd)
                    print(f"Wysłano: {response}")
                else:
                    print(f"Błąd: FIFO klienta nie istnieje: {client_fifo_path}")

            except (ValueError, OSError) as e:
                print(f"Błąd: {e}")
                
    finally:
        if fifo:
            fifo.close()
        if fifo_write != -1:
            os.close(fifo_write)
        if os.path.exists(SERVER_FIFO):
            os.unlink(SERVER_FIFO)
        print("\nSerwer zakończony.")

if __name__ == "__main__":
    run_server()