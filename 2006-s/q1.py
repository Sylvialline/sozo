from pathlib import Path
HERE, ROOT = Path(__file__).resolve().parents[:2]
DATA = HERE/"data"

def caesar(text: str, shift: int) -> str:
    res = []
    for c in text:
        d = c
        if c.isalpha():
            base = ord('A') if c.isupper() else ord('a')
            offset = ord(c) - base
            d = chr(base + (offset + shift) % 26)
        res.append(d)
    return ''.join(res)

text = Path(DATA/"q1.txt").read_text()
first_line = text.split('\n')[0]
for i in range(1, 26):
    print(i, caesar(first_line, i)) 
    # key=15

print("Decrypted:\n", caesar(text, 15))