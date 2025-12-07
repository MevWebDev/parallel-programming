

import socket


serwerAdresPort   = ("127.0.0.1", 5001)
bufSize = 1024

UDPClientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("Klient gotowy. Wpisz: k (kamien), p (papier), n (nozyce) lub 'koniec'.")

points = 0

while True:
    kom = input("Twoj wybor: ")
    UDPClientSocket.sendto(kom.encode(), serwerAdresPort)
    
    if kom == "koniec":
        break
    try:
        data, addr = UDPClientSocket.recvfrom(bufSize)
        if data.decode() == "win":
            print("Wygrales!")
            points += 1
        elif data.decode() == "lose":
            print("Przegrales!")
        elif data.decode() == "remis":
            print("Remis!")
        else:
            print(data.decode())
            break

        print(f"Twoje punkty: {points}")
    except Exception as e:
        print(f"Blad odbioru: {e}")
        break



