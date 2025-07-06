import socket
import threading

HOST = '0.0.0.0'
PORT = 9005

clients = {}           # client_id -> socket
nicknames = {}         # client_id -> nickname
next_id = 1            # 다음 클라이언트 ID
lock = threading.Lock()

# 클라이언트마다 별도의 파일 객체로 라인 단위 읽기

def recv_line(conn):
    buffer = b''
    while True:
        chunk = conn.recv(1)
        if not chunk:
            return None
        buffer += chunk
        if buffer.endswith(b"\r\n"):
            return buffer.decode().strip()


def broadcast(sender_id, msg):
    with lock:
        for cid, sock in clients.items():
            if cid != sender_id:
                sock.sendall(msg.encode())


def handle_client(conn, addr):
    global next_id
    with lock:
        client_id = next_id
        next_id += 1
        clients[client_id] = conn

    try:
        # 1) JOIN 처리
        line = recv_line(conn)
        if not line or not line.startswith('JOIN '):
            conn.sendall(b"400 ERR Invalid JOIN. Use: JOIN <nickname>\r\n")
            return
        nickname = line.split(' ', 1)[1]
        with lock:
            nicknames[client_id] = nickname
        conn.sendall(f"100 WELCOME {client_id} {nickname}\r\n".encode())

        # 2) 메시지 루프
        while True:
            line = recv_line(conn)
            if not line:
                break
            parts = line.split(' ', 2)
            cmd = parts[0]

            if cmd == 'LIST':
                with lock:
                    lst = ','.join(f"{cid}:{nick}" for cid, nick in nicknames.items())
                conn.sendall(f"101 LIST {lst}\r\n".encode())

            elif cmd == 'BROADCAST' and len(parts) >= 2:
                msg = parts[1]
                out = f"200 MSG {client_id}:{nickname} {msg}\r\n"
                broadcast(client_id, out)

            elif cmd == 'MSG' and len(parts) >= 3:
                target_id = int(parts[1])
                msg = parts[2]
                with lock:
                    target_sock = clients.get(target_id)
                if target_sock:
                    target_sock.sendall(f"200 MSG {client_id}:{nickname} {msg}\r\n".encode())
                else:
                    conn.sendall(b"400 ERR No such client\r\n")

            elif cmd == 'QUIT':
                conn.sendall(f"221 BYE {client_id}\r\n".encode())
                break

            else:
                conn.sendall(b"400 ERR Unknown command\r\n")

    finally:
        with lock:
            clients.pop(client_id, None)
            nicknames.pop(client_id, None)
        conn.close()
        print(f"[서버] 클라이언트 {addr} ({client_id}) 연결 종료")


def main():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((HOST, PORT))
    server_sock.listen()
    print(f"[서버] {HOST}:{PORT} 대기 중...")

    try:
        while True:
            conn, addr = server_sock.accept()
            print(f"[서버] 연결 수락: {addr}")
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
    except KeyboardInterrupt:
        print("\n[서버] 종료 중...")
    finally:
        server_sock.close()

if __name__ == '__main__':
    main()