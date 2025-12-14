# Wyjaśnienie kodu `zad3.py` (Notatki dla studenta)

Ten dokument wyjaśnia działanie programu `zad3.py` krok po kroku. Użyj tych notatek, aby wytłumaczyć kod prowadzącemu.

## 1. Co robi ten program?
Program zlicza wystąpienia konkretnego słowa (np. "Stoi") w pliku tekstowym.
**Kluczowa cecha**: Jeśli w pliku znajduje się dyrektywa `\input{inny_plik.txt}`, program:
1.  Wykrywa to.
2.  Tworzy **nowy proces** (dziecko), aby policzyć słowa w tym zagnieżdżonym pliku.
3.  Sumuje wyniki z pliku głównego i plików podrzędnych.

---

## 2. Kluczowe funkcje

### `count_word_occurrences(target_word, line_text)`
*   **Cel**: Policz ile razy słowo występuje w jednej linii.
*   **Jak działa**:
    1.  Zamienia wszystkie znaki niebędące literami na spacje (żeby oddzielić słowa, np. "dom," -> "dom ").
    2.  Zamienia wszystko na małe litery (ignoruje wielkość liter).
    3.  Dzieli tekst na listę słów (`split()`).
    4.  Zlicza wystąpienia szukanego słowa.

### `extract_filename_from_directive(text_line, directive_marker)`
*   **Cel**: Sprawdza, czy linia zawiera `\input{...}` i wyciąga nazwę pliku ze środka nawiasów.
*   **Działanie**: Proste operacje na stringach (`find`, wycinanie fragmentu).

---

## 3. Główna logika: `analyze_file_recursive`

To serce programu. Funkcja przyjmuje ścieżkę do pliku i szukane słowo.

### Przebieg działania:
1.  Otwiera plik i czyta go linia po linii.
2.  Dla każdej linii sprawdza:
    *   **Czy to zwykły tekst?** -> Zlicza słowa funkcją `count_word_occurrences`.
    *   **Czy to `\input{...}`?** -> Jeśli tak, uruchamia mechanizm procesów.

### Mechanizm procesów (`os.fork()`) - NAJWAŻNIEJSZE!
Gdy program napotka `\input{plikB.txt}`, nie wywołuje po prostu funkcji rekurencyjnie w tym samym procesie. Zamiast tego:

1.  **`pid = os.fork()`**: System operacyjny klonuje obecny proces. Od tego momentu działają dwa identyczne programy (Rodzic i Dziecko).
2.  **Rozróżnienie procesów**:
    *   Jeśli `pid == 0`: Jesteśmy w **DZIECKU**.
    *   Jeśli `pid > 0`: Jesteśmy w **RODZICU** (a `pid` to numer ID dziecka).

#### Co robi Dziecko (`pid == 0`)?
1.  Wywołuje rekurencyjnie `analyze_file_recursive` dla nowego pliku.
2.  **Ważne**: Kończy działanie funkcją **`os._exit(wynik)`**.
    *   Dlaczego `os._exit` a nie `sys.exit`? Bo to proces potomny, musi natychmiast oddać sterowanie do systemu, nie czyszcząc buforów rodzica.
    *   **Ograniczenie**: `os._exit` zwraca kod wyjścia (exit code), który w systemach Unix jest liczbą 0-255. Jeśli słów będzie więcej niż 255, wynik będzie błędny (modulo 256)!

#### Co robi Rodzic (`pid > 0`)?
1.  Czeka na zakończenie dziecka: **`os.waitpid(pid, 0)`**. To blokuje rodzica, dopóki dziecko nie skończy.
2.  Odbiera status zakończenia.
3.  Wyciąga wynik z kodu wyjścia dziecka: **`os.WEXITSTATUS(status)`**.
4.  Dodaje ten wynik do swojej sumy słów.

---

## 4. Podsumowanie w punktach (ściąga)
*   **Rekurencja**: Tak, ale realizowana przez nowe procesy.
*   **Komunikacja**: Dziecko zwraca wynik jako "kod błędu" (`exit code`).
*   **Synchronizacja**: Rodzic czeka na dziecko (`waitpid`), więc zliczanie jest sekwencyjne (drzewo wywołań), a nie równoległe w sensie "wszystko naraz".
*   **Ograniczenia**: Kod wyjścia to tylko 1 bajt (0-255). To jest "hack" dydaktyczny, w prawdziwym kodzie użylibyśmy `multiprocessing.Queue` lub `Pipe`.
