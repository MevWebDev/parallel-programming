import sysv_ipc
import sys
import time

# Stałe klucze dla zasobów IPC
BASE_KEY = 2000
NULL_CHAR = '\0'

# Funkcje pomocnicze do obsługi pamięci współdzielonej
def write_to_shared_memory(memory, text):
    """Zapisuje ciąg znaków do pamięci współdzielonej."""
    text += NULL_CHAR
    text_encoded = text.encode()
    memory.write(text_encoded)

def read_from_shared_memory(memory):
    """Odczytuje ciąg znaków z pamięci współdzielonej."""
    data = memory.read()
    text = data.decode()
    null_index = text.find(NULL_CHAR)
    if null_index != -1:
        text = text[:null_index]
    return text

def main():
    # Klucze dla poszczególnych zasobów IPC
    # Używamy stałych kluczy, aby oba procesy mogły się odnaleźć
    key_memory_player1 = BASE_KEY + 1  # Pamięć dla Gracza 1
    key_memory_player2 = BASE_KEY + 2  # Pamięć dla Gracza 2
    key_sem_p1_wrote   = BASE_KEY + 3  # Semafor: Gracz 1 zapisał
    key_sem_p2_wrote   = BASE_KEY + 4  # Semafor: Gracz 2 zapisał
    key_sem_p1_read    = BASE_KEY + 5  # Semafor: Gracz 1 odczytał
    key_sem_p2_read    = BASE_KEY + 6  # Semafor: Gracz 2 odczytał

    player_number = 0
    
    # Zmienne na zasoby
    shared_memory_p1 = None
    shared_memory_p2 = None
    sem_p1_wrote = None 
    sem_p2_wrote = None 
    sem_p1_read = None 
    sem_p2_read = None 

    try:
        # Próba utworzenia pamięci współdzielonej dla Gracza 1 z flagą IPC_CREX.
        # Jeśli się uda (nie ma błędu), to znaczy, że jesteśmy pierwszym procesem -> Gracz 1.
        shared_memory_p1 = sysv_ipc.SharedMemory(key_memory_player1, sysv_ipc.IPC_CREX, mode=0o600, size=1024)
        print("Jestem Gracz 1")
        player_number = 1
        
        # Gracz 1 tworzy pozostałe zasoby (pamięć dla G2 i semafory)
        shared_memory_p2 = sysv_ipc.SharedMemory(key_memory_player2, sysv_ipc.IPC_CREAT, mode=0o600, size=1024)
        
        # Tworzenie semaforów z wartością początkową 0 (zablokowane)
        sem_p1_wrote = sysv_ipc.Semaphore(key_sem_p1_wrote, sysv_ipc.IPC_CREAT, initial_value=0)
        sem_p2_wrote = sysv_ipc.Semaphore(key_sem_p2_wrote, sysv_ipc.IPC_CREAT, initial_value=0)
        sem_p1_read  = sysv_ipc.Semaphore(key_sem_p1_read, sysv_ipc.IPC_CREAT, initial_value=0)
        sem_p2_read  = sysv_ipc.Semaphore(key_sem_p2_read, sysv_ipc.IPC_CREAT, initial_value=0)

    except sysv_ipc.ExistentialError:
        # Jeśli pamięć już istnieje (błąd ExistentialError), to znaczy, że Gracz 1 już działa.
        # Zatem my jesteśmy Graczem 2.
        print("Jestem Gracz 2")
        player_number = 2
        
        # Gracz 2 podłącza się do istniejących zasobów utworzonych przez Gracza 1
        shared_memory_p1 = sysv_ipc.SharedMemory(key_memory_player1)
        shared_memory_p2 = sysv_ipc.SharedMemory(key_memory_player2)
        sem_p1_wrote = sysv_ipc.Semaphore(key_sem_p1_wrote)
        sem_p2_wrote = sysv_ipc.Semaphore(key_sem_p2_wrote)
        sem_p1_read  = sysv_ipc.Semaphore(key_sem_p1_read)
        sem_p2_read  = sysv_ipc.Semaphore(key_sem_p2_read)

    wins = 0
    
    try:
        # Pętla gry - 3 tury
        for turn in range(1, 4):
            print(f"\n--- Tura {turn} ---")
            
            my_choice = ""
            opponent_choice = ""
            
            if player_number == 1:
                # --- RUCH GRACZA 1 ---
                
                # 1. Gracz 1 wybiera kartę
                while True:
                    my_choice = input("Podaj pozycję wygrywającej karty (1-3): ").strip()
                    if my_choice in ['1', '2', '3']:
                        break
                    print("Nieprawidłowy wybór.")
                
                # Zapis wyboru do pamięci współdzielonej PW1
                write_to_shared_memory(shared_memory_p1, my_choice)
                
                # Sygnalizacja: Gracz 1 zapisał dane (podnosi semafor 1)
                sem_p1_wrote.release() 
                
                print("Czekam na ruch Gracza 2...")
                # Oczekiwanie: Aż Gracz 2 zapisze swój wybór (opuszcza semafor 2)
                sem_p2_wrote.acquire() 
                
                # 3. Gracz 1 odczytuje wybór Gracza 2 z pamięci PW2
                opponent_choice = read_from_shared_memory(shared_memory_p2)
                print(f"Gracz 2 wybrał: {opponent_choice}")
                print(f"Mój wybór: {my_choice}")
                
                # Sprawdzenie wyniku tury
                if my_choice == opponent_choice:
                    print("Wygrał Gracz 2!")
                else:
                    print("Wygrał Gracz 1!")
                    wins += 1
                
                # Sygnalizacja: Gracz 1 zakończył odczyt (podnosi semafor 3)
                sem_p1_read.release() 
                
                print("Czekam na zakończenie tury przez Gracza 2...")
                # Bariera synchronizacyjna: Czekamy aż Gracz 2 też zakończy odczyt (opuszcza semafor 4)
                # To zapewnia, że nie przejdziemy do nowej tury, dopóki obie strony nie skończą obecnej.
                sem_p2_read.acquire() 
                
            else: # Gracz 2
                # --- RUCH GRACZA 2 ---
                
                print("Czekam na ruch Gracza 1...")
                # Oczekiwanie: Aż Gracz 1 zapisze swój wybór (opuszcza semafor 1)
                sem_p1_wrote.acquire() 
                
                # 2. Gracz 2 zgaduje pozycję
                while True:
                    my_choice = input("Zgadnij pozycję wygrywającej karty (1-3): ").strip()
                    if my_choice in ['1', '2', '3']:
                        break
                    print("Nieprawidłowy wybór.")
                
                # Zapis wyboru do pamięci współdzielonej PW2
                write_to_shared_memory(shared_memory_p2, my_choice)
                
                # Sygnalizacja: Gracz 2 zapisał dane (podnosi semafor 2)
                sem_p2_wrote.release() 
                
                print("Czekam na odczyt mojego wyboru przez Gracza 1...")
                # Oczekiwanie: Aż Gracz 1 odczyta wybór Gracza 2 (opuszcza semafor 3)
                # Jest to konieczne, aby Gracz 1 zdążył przeczytać PW2 zanim Gracz 2 przejdzie dalej.
                sem_p1_read.acquire() 
                
                # 4. Gracz 2 odczytuje wybór Gracza 1 z pamięci PW1
                opponent_choice = read_from_shared_memory(shared_memory_p1)
                print(f"Gracz 1 wybrał: {opponent_choice}")
                print(f"Mój wybór: {my_choice}")
                
                # Sprawdzenie wyniku tury
                if opponent_choice == my_choice:
                    print("Wygrał Gracz 2!")
                    wins += 1
                else:
                    print("Wygrał Gracz 1!")
                
                # Sygnalizacja: Gracz 2 zakończył odczyt (podnosi semafor 4)
                # To zwalnia barierę dla Gracza 1.
                sem_p2_read.release() 

        # Podsumowanie gry po 3 turach
        print("\n--- Koniec gry ---")
        if player_number == 1:
            print(f"Wynik sumaryczny: Gracz 1 wygrał {wins} razy.")
        else:
            print(f"Wynik sumaryczny: Gracz 2 wygrał {wins} razy.")

    except Exception as e:
        print(f"Wystąpił błąd: {e}")
    finally:
        # Sprzątanie zasobów - wykonuje tylko Gracz 1 (właściciel)
        if player_number == 1:
            print("Usuwanie zasobów...")
            try:
                shared_memory_p1.remove()
                shared_memory_p2.remove()
                sem_p1_wrote.remove()
                sem_p2_wrote.remove()
                sem_p1_read.remove()
                sem_p2_read.remove()
            except:
                pass

if __name__ == "__main__":
    main()
