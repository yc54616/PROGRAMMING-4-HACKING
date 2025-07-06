import socket 
import threading

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

SERVER_IP = "127.0.0.1"
SERVER_PORT = 1234

client.connect((SERVER_IP, SERVER_PORT))

def recv_thread():
    while True:
        try:
            data = client.recv(1024)
            if not data:
                print("서버가 연결을 종료했습니다.")
                break
            msg = data.decode()
            print(f"서버: {msg}")
        except Exception as e:
            print(f"오류 발생: {e}")
            break

def send_thread():
    while True:
        try:
            response = input("클라이언트: ")
            client.sendall(response.encode())
        except Exception as e:
            print(f"오류 발생: {e}")
            break

threading.Thread(target=recv_thread, daemon=True).start()
threading.Thread(target=send_thread, daemon=True).start()

try:
    while threading.active_count() > 1:
        pass
except KeyboardInterrupt:
    print("클라이언트를 종료합니다.")
finally:
    client.close()
    print("클라이언트가 종료되었습니다.")