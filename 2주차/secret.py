xor = bytes.fromhex("73626960647f6b206821204f21254f7d694f7624662065622127234f726927756d")

for i in range(0x00, 0xff+1):
    for j in range(len(xor)):
        print(chr(xor[j] ^ i), end="")
    print()