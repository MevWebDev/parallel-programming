import socket

IP     = "127.0.0.1"
port   = 5001
bufSize  = 1024

UDPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    UDPServerSocket.bind((IP, port))
except OSError:
    print(f"Port {port} zajety. Upewnij sie, ze poprzedni serwer zostal zatrzymany.")
    exit(1)

print("serwer UDP dziala")

players = []
moves = {}
score1 = 0
score2 = 0

def checkRockPaperScissors(choice1, choice2):
    if choice1 == choice2:
        return "Remis"
    elif (choice1 == "k" and choice2 == "n") or (choice1 == "p" and choice2 == "k") or (choice1 == "n" and choice2 == "p"):
        return 1
    else:
        return 2

while True:
    try:
        data, addr = UDPServerSocket.recvfrom(bufSize)
        msg = data.decode().strip() # strip whitespace just in case

        # Logika rejestracji
        if addr not in players:
            if len(players) < 2:
                players.append(addr)
                print(f"Gracz dolaczyl: {addr}")
            else:
                # Opcjonalnie: informacja dla 3 gracza ze serwer pelny
                UDPServerSocket.sendto("Serwer pelny".encode(), addr)
                continue

        # Obsluga komendy koniec
        if msg == "koniec":
            for p in players:
                UDPServerSocket.sendto("Koniec gry".encode(), p)
            players = []
            moves = {}
            score1 = 0
            score2 = 0
            print("Zresetowano gre.")
            continue

        # Zapis ruchu
        if addr in players:
            moves[addr] = msg
            
        # Sprawdz czy mamy ruchy obu graczy
        if len(players) == 2 and len(moves) == 2:
            p1 = players[0]
            p2 = players[1]
            
            c1 = moves[p1]
            c2 = moves[p2]
            
            res = checkRockPaperScissors(c1, c2)
            
            if res == 1:
                score1 += 1
                msg1 = "win"
                msg2 = "lose"
            elif res == 2:
                score2 += 1
                msg1 = "lose"
                msg2 = "win"
            elif res == "Remis":
                msg1 = "remis"
                msg2 = "remis"

            print(f"Zwycięzca: Gracz {res} (Gracz1: {c1}, Gracz2: {c2})")
            print(f"Wynik: {score1} - {score2}")

            # Wyslanie wynikow
            UDPServerSocket.sendto(msg1.encode(), p1)
            UDPServerSocket.sendto(msg2.encode(), p2)
            
            # Reset ruchow na kolejna runde
            moves = {}
            
    except Exception as e:
        print(f"Blad: {e}")
