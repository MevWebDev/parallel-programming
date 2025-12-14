import threading
import random

threads = 8
N = 5

# Generate a much longer list with random numbers
random.seed(42)  # For reproducibility
L = [random.randint(0, N-1) for _ in range(1000)]

results = {}


def countOccurencies(L, N, thread_id):
    """Count occurrences of numbers in the list segment"""
    result = [0] * N
    for number in L:
        if number < N: 
            result[number] += 1
    results[thread_id] = result

def main():
    chunk_size = len(L) // threads
    
    thread_list = []
    for i in range(threads):
        start = i * chunk_size
        end = (i + 1) * chunk_size if i < threads - 1 else len(L)
        
        thread_segment = L[start:end]
        t = threading.Thread(target=countOccurencies, args=(thread_segment, N, i))
        thread_list.append(t)
        t.start()
        
    
    for t in thread_list:
        t.join()

    final_result = [0] * N
    for thread_id in range(threads):
        print(f"Thread {thread_id} counting: {results[thread_id]}")
        for i in range(N):
            final_result[i] += results[thread_id][i]

    print(f"\nList length: {len(L)}")
    print(f"Final count: {final_result}")

main()



