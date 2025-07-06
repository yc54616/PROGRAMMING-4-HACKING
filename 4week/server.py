import socket
import threading

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

HOST = '0.0.0.0'
PORT = 1234

server.bind((HOST, PORT))
server.listen(1)

conn,addr = server.accept()
print(f'Connected by {addr}')

def recv_thread():
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                print("클라이언트가 연결을 종료했습니다.")
                break
            msg = data.decode()
            print(f"클라이언트: {msg}")
        except Exception as e:
            print(f"오류 발생: {e}")
            break

def send_thread():
    while True:
        try:
            response = input("서버: ")
            conn.sendall(response.encode())
        except Exception as e:
            print(f"오류 발생: {e}")
            break

threading.Thread(target=recv_thread, daemon=True).start()
threading.Thread(target=send_thread, daemon=True).start()

try:
    while threading.active_count() > 1:
        pass
except KeyboardInterrupt:
    print("서버를 종료합니다.")
finally:
    conn.close()
    server.close()
    print("서버가 종료되었습니다.")