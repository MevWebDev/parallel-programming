import os 
import sys 

# Definicja markera dyrektywy input
INPUT_DIRECTIVE = r'\input{'

def count_word_occurrences(target_word, line_text):
    """
    Zlicza wystąpienia słowa w linii tekstu.
    Ignoruje wielkość liter i znaki niealfabetyczne.
    """
    normalized_chars = [ch.lower() if ch.isalpha() else " " for ch in line_text]
    words_list = ''.join(normalized_chars).split()
    return words_list.count(target_word.lower())

def extract_filename_from_directive(text_line, directive_marker):
    """
    Sprawdza, czy linia zawiera dyrektywę \input{} i zwraca nazwę pliku.
    Jeśli nie znaleziono, zwraca False.
    """
    if directive_marker not in text_line:
        return False
    
    begin = text_line.find(directive_marker) + len(directive_marker)
    end = text_line.find('}', begin)
    
    if end == -1:
        return False
    
    return text_line[begin:end]

def analyze_file_recursive(file_path, search_term):
    """
    Analizuje plik rekurencyjnie, zliczając wystąpienia szukanego słowa.
    Tworzy procesy potomne dla zagnieżdżonych plików.
    """
    word_count = 0
    
    try:
        with open(file_path, 'r', encoding='utf-8') as input_file:
            for current_line in input_file:
                stripped_line = current_line.strip()
                
                # Sprawdź, czy linia zawiera dyrektywę input
                nested_file = extract_filename_from_directive(stripped_line, INPUT_DIRECTIVE)
                
                if nested_file is False:
                    # Zwykła linia - zlicz słowa
                    occurrences = count_word_occurrences(search_term, stripped_line)
                    word_count += occurrences
                    print(stripped_line)
                    
                elif os.path.isfile(nested_file):
                    # Znaleziono zagnieżdżony plik - utwórz proces potomny
                    process_id = os.fork()
                    
                    if process_id == 0:
                        # Kod wykonywany przez proces potomny
                        try:
                            _, child_word_count = analyze_file_recursive(nested_file, search_term)
                            os._exit(child_word_count)
                        except Exception as error:
                            print(f"Błąd przetwarzania {nested_file}: {error}", 
                                  file=sys.stderr, flush=True)
                            os._exit(1)
                    else:
                        # Kod wykonywany przez proces rodzica
                        try:
                            # Oczekiwanie na zakończenie procesu potomnego
                            _, exit_status = os.waitpid(process_id, 0)
                            
                            if os.WIFEXITED(exit_status):
                                child_result = os.WEXITSTATUS(exit_status)
                                word_count += child_result
                                
                        except ChildProcessError as error:
                            print(f"Błąd oczekiwania na proces {process_id}: {error}", 
                                  file=sys.stderr, flush=True)
                                  
    except FileNotFoundError:
        print(f"BŁĄD: Nie znaleziono pliku: {file_path}", 
              file=sys.stderr, flush=True)
    except IOError as error:
        print(f"BŁĄD I/O dla pliku {file_path}: {error}", 
              file=sys.stderr, flush=True)
    
    return file_path, word_count


if __name__ == "__main__":
    # Główna część programu
    word_to_search = "Stoi"
    main_file = 'plikA.txt'
    
    print(f"Rozpoczynam zliczanie wystąpień słowa '{word_to_search}':\n")
    
    processed_file, total_occurrences = analyze_file_recursive(main_file, word_to_search)
    
    print(f"{'-'*50}")
    print(f"Całkowita liczba wystąpień słowa '{word_to_search}': {total_occurrences}")
    