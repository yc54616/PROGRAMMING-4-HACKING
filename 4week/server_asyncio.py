import asyncio

HOST = '0.0.0.0'
PORT = 9005

clients = {}       # client_id -> writer
nicknames = {}
next_id = 1
lock = asyncio.Lock()

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    global next_id
    # 1) 할당 및 JOIN 처리
    async with lock:
        client_id = next_id
        next_id += 1
        clients[client_id] = writer

    # 받기 함수
    async def recv_line():
        data = await reader.readuntil(b'\r\n')
        return data.decode().strip()

    # JOIN
    line = await recv_line()
    if not line.startswith('JOIN '):
        writer.write(b'400 ERR Invalid JOIN\r\n')
        await writer.drain()
        writer.close()
        return

    nickname = line.split(' ',1)[1]
    async with lock:
        nicknames[client_id] = nickname
    writer.write(f'100 WELCOME {client_id} {nickname}\r\n'.encode())
    await writer.drain()

    # 2) 메시지 루프
    try:
        while True:
            line = await recv_line()
            parts = line.split(' ', 2)
            cmd = parts[0]

            # LIST
            if cmd == 'LIST':
                async with lock:
                    lst = ','.join(f'{cid}:{nick}' for cid, nick in nicknames.items())
                writer.write(f'101 LIST {lst}\r\n'.encode())

            # BROADCAST
            elif cmd == 'BROADCAST' and len(parts) > 1:
                msg = parts[1]
                out = f'200 MSG {client_id}:{nickname} {msg}\r\n'
                async with lock:
                    for cid, w in clients.items():
                        if cid != client_id:
                            w.write(out.encode())

            # MSG (1:1)
            elif cmd == 'MSG' and len(parts) > 2:
                target = int(parts[1])
                msg = parts[2]
                async with lock:
                    w = clients.get(target)
                if w:
                    w.write(f'200 MSG {client_id}:{nickname} {msg}\r\n'.encode())
                else:
                    writer.write(b'400 ERR No such client\r\n')

            # QUIT
            elif cmd == 'QUIT':
                writer.write(f'221 BYE {client_id}\r\n'.encode())
                break

            else:
                writer.write(b'400 ERR Unknown command\r\n')

            await writer.drain()

    except asyncio.IncompleteReadError:
        pass  # 클라이언트 비정상 종료

    # 정리
    async with lock:
        clients.pop(client_id, None)
        nicknames.pop(client_id, None)
    writer.close()
    await writer.wait_closed()

async def main():
    server = await asyncio.start_server(handle_client, HOST, PORT)
    addr = server.sockets[0].getsockname()
    print(f'[서버] Serving on {addr}')

    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(main())
