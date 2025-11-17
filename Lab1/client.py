
"""Prosty klient komunikujący się przez pliki.

Klient pyta użytkownika o liczbę całkowitą, zapisuje ją do pliku 'dane',
a następnie czeka aż serwer zapisze wynik do pliku 'wyniki'.
"""
import os
import sys
import time

ROOT = os.path.dirname(__file__)

DATA = os.path.join(ROOT, 'dane')
RESULT = os.path.join(ROOT, 'wyniki')


for p in (DATA, RESULT):
    try:
        open(p, 'a', encoding='utf-8').close()
    except Exception:
        pass


def atomic_write(path: str, text: str):
    """Zapis atomowy: najpierw plik tymczasowy, potem zamiana."""
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(text)
    os.replace(tmp, path)


def read_file_if_nonempty(path: str):
    """Zwraca zawartość pliku jeśli niepusty, w przeciwnym razie None."""
    if not os.path.exists(path):
        return None
    try:
        if os.path.getsize(path) == 0:
            return None
    except OSError:
        return None
    with open(path, 'r', encoding='utf-8') as f:
        s = f.read().strip()
    return s if s != '' else None


def main():
    

    try:
        x = input('Podaj liczbę całkowitą: ').strip()
        int(x)  
    except Exception:
        print('Niepoprawna liczba')
        sys.exit(1)

    
    try:
        atomic_write(RESULT, '')
    except Exception:
        pass

    atomic_write(DATA, x + '\n')
    print('Zapisano żądanie, oczekiwanie na odpowiedź serwera...')

   
    start = time.time()
    while True:
        s = read_file_if_nonempty(RESULT)
        if s is not None:
            print('Wynik od serwera:', s)
         
            break
        time.sleep(0.1)
        
        if time.time() - start > 30:
            print('Przekroczono czas oczekiwania na serwer.')
            break


if __name__ == '__main__':
    main()
