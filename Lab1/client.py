#!/usr/bin/env python3
"""Prosty klient komunikujący się przez pliki.

Klient pyta użytkownika o liczbę całkowitą, zapisuje ją do pliku 'dane',
a następnie czeka aż serwer zapisze wynik do pliku 'wyniki'.
"""
import os
import sys
import time

ROOT = os.path.dirname(__file__)
# pliki w katalogu repozytorium: 'dane' i 'wyniki'
DATA = os.path.join(ROOT, 'dane')
RESULT = os.path.join(ROOT, 'wyniki')

# ensure files exist
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
    # files are created at module import; no directory check needed

    try:
        x = input('Podaj liczbę całkowitą: ').strip()
        int(x)  # walidacja
    except Exception:
        print('Niepoprawna liczba')
        sys.exit(1)

    # ensure we start with an empty result file so we don't read stale data
    try:
        atomic_write(RESULT, '')
    except Exception:
        pass

    atomic_write(DATA, x + '\n')
    print('Zapisano żądanie, oczekiwanie na odpowiedź serwera...')

    # aktywne oczekiwanie (busy-wait) na wynik
    start = time.time()
    while True:
        s = read_file_if_nonempty(RESULT)
        if s is not None:
            print('Wynik od serwera:', s)
            # Nie czyścimy pliku 'wyniki' po odczycie — tak, żeby było widać
            # żądanie i odpowiedź podczas prezentacji.
            break
        time.sleep(0.1)
        # limit czasu oczekiwania (opcjonalnie) -- 30s
        if time.time() - start > 30:
            print('Przekroczono czas oczekiwania na serwer.')
            break


if __name__ == '__main__':
    main()
