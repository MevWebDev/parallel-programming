import os
import glob
import time

# Znajdź najwyższy numer istniejącego pliku clientFile*
existing_files = glob.glob("clientFile*")
if existing_files:
    numbers = [int(f.replace("clientFile", "")) for f in existing_files if f.replace("clientFile", "").isdigit()]
    next_number = max(numbers) + 1 if numbers else 1
else:
    next_number = 1

# Plik konwersacji dla tego klienta
conversation_file = f"clientFile{next_number}"

# Jeśli plik istnieje, wyświetl historię konwersacji
if os.path.exists(conversation_file):
    print(f"\n=== Historia konwersacji (Klient {next_number}) ===")
    with open(conversation_file, "r") as f:
        print(f.read())
    print("=" * 40)
else:
    # Utwórz nowy plik konwersacji
    with open(conversation_file, "w") as f:
        f.write("")
    print(f"Utworzono nowy plik konwersacji: {conversation_file}")

# Pętla rozmowy
while True:
    # Poproś użytkownika o wpisanie wiadomości
    user_input = input("\nWpisz wiadomość do serwera (lub 'exit' aby zakończyć): ")
    
    if user_input.lower() == 'exit':
        print("Kończenie rozmowy...")
        break
    
    # Sprawdź, czy serwer jest zajęty
    if os.path.exists("lockFile"):
        print("⚠️  Serwer jest zajęty obsługą innego klienta. Proszę czekać...")
        # Czekaj aż serwer się zwolni
        while os.path.exists("lockFile"):
            time.sleep(0.5)
        print("✓ Serwer jest teraz dostępny.")
    
    # Zapisz wiadomość do pliku konwersacji (append)
    with open(conversation_file, "a") as f:
        f.write(f"Klient {next_number}: {user_input}\n")
    
    print(f"Wiadomość wysłana, czekam na odpowiedź serwera...")
    
    # Policz ile linii było przed wysłaniem
    with open(conversation_file, "r") as f:
        lines_before = len(f.readlines())
    
    # Czekaj na odpowiedź serwera (nowa linia w pliku)
    timeout = 60  # 60 sekund timeout
    start_time = time.time()
    
    while True:
        if time.time() - start_time > timeout:
            print("Timeout - serwer nie odpowiedział.")
            break
        
        if os.path.exists(conversation_file):
            with open(conversation_file, "r") as f:
                lines = f.readlines()
                if len(lines) > lines_before:
                    # Nowa odpowiedź od serwera
                    print("\n=== Odpowiedź serwera ===")
                    for line in lines[lines_before:]:
                        print(line.strip())
                    break
        
        time.sleep(0.5)

print("\nRozmowa zakończona.")