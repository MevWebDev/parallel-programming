import os
import time
import glob

print("Serwer uruchomiony. Czekam na wiadomości od klientów...")

# Słownik do śledzenia ostatniej przetworzonej linii dla każdego pliku
last_processed = {}

while True:
    # Sprawdź, czy istnieją pliki clientFile*
    client_files = glob.glob("clientFile*")
    if client_files:
        # Filtruj pliki z poprawnymi numerami
        valid_files = [(f, os.path.getmtime(f)) for f in client_files if f.replace("clientFile", "").isdigit()]
        
        for file_path, _ in valid_files:
            number = int(file_path.replace("clientFile", ""))
            
            # Przeczytaj plik
            with open(file_path, "r") as f:
                lines = f.readlines()
            
            # Sprawdź, ile linii już przetworzyliśmy
            if file_path not in last_processed:
                last_processed[file_path] = 0
            
            # Znajdź nowe wiadomości od klienta (nie przetworzone jeszcze)
            new_messages = []
            for i in range(last_processed[file_path], len(lines)):
                line = lines[i].strip()
                if line.startswith(f"Klient {number}:"):
                    new_messages.append((i, line))
            
            # Jeśli są nowe wiadomości, przetwórz pierwszą
            if new_messages:
                line_index, message = new_messages[0]
                
                # Utwórz plik zamkowy (lockFile)
                with open("lockFile", "w") as lock:
                    lock.write("")
                
                print(f"\n=== Nowa wiadomość od Klienta {number} ===")
                print(f"Otrzymano: {message}")
                
                # Poproś operatora serwera o odpowiedź
                response = input("Wpisz odpowiedź dla klienta: ")
                
                # Zapisz odpowiedź do pliku klienta (append)
                with open(file_path, "a") as f:
                    f.write(f"Serwer: {response}\n")
                
                print(f"Odpowiedź wysłana do {file_path}")
                
                # Zaktualizuj ostatnią przetworzoną linię
                last_processed[file_path] = len(lines)
                
                # Usuń plik zamkowy
                os.remove("lockFile")
                print("LockFile usunięty, gotowy na następne żądanie\n")
                
                # Przetwarzaj tylko jedną wiadomość na raz
                break
    
    # Krótkie oczekiwanie przed następnym sprawdzeniem
    time.sleep(0.1)