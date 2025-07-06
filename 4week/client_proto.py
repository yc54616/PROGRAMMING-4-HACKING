import socket
import threading
import sys

HOST = '127.0.0.1'
PORT = 9005

nickname = input("닉네임을 입력하세요: ")

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

# 파일 객체로 라인 단위 읽기
file = sock.makefile('r')

# JOIN 요청
sock.sendall(f"JOIN {nickname}\r\n".encode())
# 서버 환영 메시지 수신
print(file.readline().strip())

# 수신 스레드
def recv_thread():
    while True:
        line = file.readline()
        if not line:
            print("[클라이언트] 서버 연결 종료")
            break
        print(line.strip())

# 송신 스레드
def send_thread():
    try:
        while True:
            msg = sys.stdin.readline().rstrip('\n')
            if msg.lower() == '/quit':
                sock.sendall(b"QUIT\r\n")
                break
            if msg.startswith('@'):
                # @<id> 메시지 (1:1)
                parts = msg.split(' ', 1)
                target = parts[0][1:]
                text = parts[1] if len(parts)>1 else ''
                sock.sendall(f"MSG {target} {text}\r\n".encode())
            else:
                sock.sendall(f"BROADCAST {msg}\r\n".encode())
    except Exception:
        pass

threading.Thread(target=recv_thread, daemon=True).start()
threading.Thread(target=send_thread, daemon=True).start()

# 메인 스레드 대기
try:
    while threading.active_count() > 1:
        pass
except KeyboardInterrupt:
    pass
finally:
    sock.close()
    print("[클라이언트] 종료")