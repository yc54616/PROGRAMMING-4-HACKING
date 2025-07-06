t = bytes.fromhex("0e0b213f26041e480b26217f27342e175d0e070a3c5b103e2526217f27342e175d0e077e263451150104")
print(len(t))
print(chr(t[0] ^ 109)) # crypto{}
print(chr(t[1] ^ 121))
print(chr(t[2] ^ 88))
print(chr(t[3] ^ 79))
print(chr(t[4] ^ 82))
print(chr(t[5] ^ 107))
print(chr(t[6] ^ 101))
print(chr(t[7] ^ 121))

key = [109, 121, 88, 79, 82, 107, 101, 121]

# myXORkey

for i, c in enumerate(t):
    print(chr(key[i%8] ^ c), end="")
