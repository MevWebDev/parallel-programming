
"""Prosty serwer komunikujący się przez pliki.

Serwer w pętli sprawdza plik 'dane' i zapisuje wynik do pliku 'wyniki'.
"""
import os
import time
import sys

ROOT = os.path.dirname(__file__)

DATA = os.path.join(ROOT, 'dane')
RESULT = os.path.join(ROOT, 'wyniki')


for p in (DATA, RESULT):
    try:
        open(p, 'a', encoding='utf-8').close()
    except Exception:
        pass


def compute(x: int) -> int:

    return x * 2


def read_file_if_nonempty(path: str):
    """Zwraca zawartość pliku (trim) jeśli niepusty, w przeciwnym razie None."""
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


def atomic_write(path: str, text: str):
    """Zapis atomowy: najpierw plik tymczasowy, potem zamiana (os.replace)."""
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(text)
    os.replace(tmp, path)




def main(poll: float = 1):
    print('Serwer uruchomiony. Oczekiwanie żądań w', DATA)
    try:
        while True:
            s = read_file_if_nonempty(DATA)
            if s is not None:
                
                try:
                    x = int(s.split()[0])
                except Exception:
                    res = f"BŁĄD: nie można sparsować liczby z '{s}'"
                else:
                    res = str(compute(x))
                atomic_write(RESULT, res + '\n')
               
            time.sleep(poll)
    except KeyboardInterrupt:
        print('\nSerwer zatrzymany.')
        sys.exit(0)


if __name__ == '__main__':
    main()
