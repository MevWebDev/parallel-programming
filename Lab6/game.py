import sysv_ipc
import sys
import time

# Stałe klucze dla zasobów IPC
KEY_BASE = 2000
NULL_CHAR = '\0'

# Funkcje pomocnicze do obsługi pamięci współdzielonej
def pisz(mem, s):
    """Zapisuje ciąg znaków do pamięci współdzielonej."""
    s += NULL_CHAR
    s = s.encode()
    mem.write(s)

def czytaj(mem):
    """Odczytuje ciąg znaków z pamięci współdzielonej."""
    s = mem.read()
    s = s.decode()
    i = s.find(NULL_CHAR)
    if i != -1:
        s = s[:i]
    return s

def main():
    # Klucze dla poszczególnych zasobów IPC
    # Używamy stałych kluczy, aby oba procesy mogły się odnaleźć
    key_shm1 = KEY_BASE + 1  # Pamięć dla Gracza 1
    key_shm2 = KEY_BASE + 2  # Pamięć dla Gracza 2
    key_sem1 = KEY_BASE + 3  # Semafor: Gracz 1 zapisał
    key_sem2 = KEY_BASE + 4  # Semafor: Gracz 2 zapisał
    key_sem3 = KEY_BASE + 5  # Semafor: Gracz 1 odczytał
    key_sem4 = KEY_BASE + 6  # Semafor: Gracz 2 odczytał

    player_num = 0
    
    # Zmienne na zasoby
    shm1 = None
    shm2 = None
    sem1 = None 
    sem2 = None 
    sem3 = None 
    sem4 = None 

    try:
        # Próba utworzenia pamięci współdzielonej dla Gracza 1 z flagą IPC_CREX.
        # Jeśli się uda (nie ma błędu), to znaczy, że jesteśmy pierwszym procesem -> Gracz 1.
        shm1 = sysv_ipc.SharedMemory(key_shm1, sysv_ipc.IPC_CREX, mode=0o600, size=1024)
        print("Jestem Gracz 1")
        player_num = 1
        
        # Gracz 1 tworzy pozostałe zasoby (pamięć dla G2 i semafory)
        shm2 = sysv_ipc.SharedMemory(key_shm2, sysv_ipc.IPC_CREAT, mode=0o600, size=1024)
        
        # Tworzenie semaforów z wartością początkową 0 (zablokowane)
        sem1 = sysv_ipc.Semaphore(key_sem1, sysv_ipc.IPC_CREAT, initial_value=0)
        sem2 = sysv_ipc.Semaphore(key_sem2, sysv_ipc.IPC_CREAT, initial_value=0)
        sem3 = sysv_ipc.Semaphore(key_sem3, sysv_ipc.IPC_CREAT, initial_value=0)
        sem4 = sysv_ipc.Semaphore(key_sem4, sysv_ipc.IPC_CREAT, initial_value=0)

    except sysv_ipc.ExistentialError:
        # Jeśli pamięć już istnieje (błąd ExistentialError), to znaczy, że Gracz 1 już działa.
        # Zatem my jesteśmy Graczem 2.
        print("Jestem Gracz 2")
        player_num = 2
        
        # Gracz 2 podłącza się do istniejących zasobów utworzonych przez Gracza 1
        shm1 = sysv_ipc.SharedMemory(key_shm1)
        shm2 = sysv_ipc.SharedMemory(key_shm2)
        sem1 = sysv_ipc.Semaphore(key_sem1)
        sem2 = sysv_ipc.Semaphore(key_sem2)
        sem3 = sysv_ipc.Semaphore(key_sem3)
        sem4 = sysv_ipc.Semaphore(key_sem4)

    wins = 0
    
    try:
        # Pętla gry - 3 tury
        for turn in range(1, 4):
            print(f"\n--- Tura {turn} ---")
            
            my_choice = ""
            opponent_choice = ""
            
            if player_num == 1:
                # --- RUCH GRACZA 1 ---
                
                # 1. Gracz 1 wybiera kartę
                while True:
                    my_choice = input("Podaj pozycję wygrywającej karty (1-3): ").strip()
                    if my_choice in ['1', '2', '3']:
                        break
                    print("Nieprawidłowy wybór.")
                
                # Zapis wyboru do pamięci współdzielonej PW1
                pisz(shm1, my_choice)
                
                # Sygnalizacja: Gracz 1 zapisał dane (podnosi semafor 1)
                sem1.release() 
                
                print("Czekam na ruch Gracza 2...")
                # Oczekiwanie: Aż Gracz 2 zapisze swój wybór (opuszcza semafor 2)
                sem2.acquire() 
                
                # 3. Gracz 1 odczytuje wybór Gracza 2 z pamięci PW2
                opponent_choice = czytaj(shm2)
                print(f"Gracz 2 wybrał: {opponent_choice}")
                print(f"Mój wybór: {my_choice}")
                
                # Sprawdzenie wyniku tury
                if my_choice == opponent_choice:
                    print("Wygrał Gracz 2!")
                else:
                    print("Wygrał Gracz 1!")
                    wins += 1
                
                # Sygnalizacja: Gracz 1 zakończył odczyt (podnosi semafor 3)
                sem3.release() 
                
                print("Czekam na zakończenie tury przez Gracza 2...")
                # Bariera synchronizacyjna: Czekamy aż Gracz 2 też zakończy odczyt (opuszcza semafor 4)
                # To zapewnia, że nie przejdziemy do nowej tury, dopóki obie strony nie skończą obecnej.
                sem4.acquire() 

            else: # Gracz 2
                # --- RUCH GRACZA 2 ---
                
                print("Czekam na ruch Gracza 1...")
                # Oczekiwanie: Aż Gracz 1 zapisze swój wybór (opuszcza semafor 1)
                sem1.acquire() 
                
                # 2. Gracz 2 zgaduje pozycję
                while True:
                    my_choice = input("Zgadnij pozycję wygrywającej karty (1-3): ").strip()
                    if my_choice in ['1', '2', '3']:
                        break
                    print("Nieprawidłowy wybór.")
                
                # Zapis wyboru do pamięci współdzielonej PW2
                pisz(shm2, my_choice)
                
                # Sygnalizacja: Gracz 2 zapisał dane (podnosi semafor 2)
                sem2.release() 
                
                print("Czekam na odczyt mojego wyboru przez Gracza 1...")
                # Oczekiwanie: Aż Gracz 1 odczyta wybór Gracza 2 (opuszcza semafor 3)
                # Jest to konieczne, aby Gracz 1 zdążył przeczytać PW2 zanim Gracz 2 przejdzie dalej.
                sem3.acquire() 
                
                # 4. Gracz 2 odczytuje wybór Gracza 1 z pamięci PW1
                opponent_choice = czytaj(shm1)
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
                sem4.release() 

        # Podsumowanie gry po 3 turach
        print("\n--- Koniec gry ---")
        if player_num == 1:
            print(f"Wynik sumaryczny: Gracz 1 wygrał {wins} razy.")
        else:
            print(f"Wynik sumaryczny: Gracz 2 wygrał {wins} razy.")

    except Exception as e:
        print(f"Wystąpił błąd: {e}")
    finally:
        # Sprzątanie zasobów - wykonuje tylko Gracz 1 (właściciel)
        if player_num == 1:
            print("Usuwanie zasobów...")
            try:
                shm1.remove()
                shm2.remove()
                sem1.remove()
                sem2.remove()
                sem3.remove()
                sem4.remove()
            except:
                pass

if __name__ == "__main__":
    main()
