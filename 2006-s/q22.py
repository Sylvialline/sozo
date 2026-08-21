from collections import Counter
import json
from pathlib import Path
from q21 import count_alpha
HERE, ROOT = Path(__file__).resolve().parents[:2]
DATA = HERE/"data"
OUTPUT = HERE / "output"
OUTPUT.mkdir(exist_ok=True)

def translate(text: str, lower_mapping: dict[str, str]):
    full_mapping = lower_mapping.copy()
    full_mapping.update((k.upper(), v.upper()) for k, v in lower_mapping.items())
    translated = text.translate(str.maketrans(full_mapping))
    return translated

def compare(cipher_text: str, decrypted_text: str):
    i = 0
    for cipher_line, decrypted_line in zip(cipher_text.split('\n'), decrypted_text.split('\n')):
        if len(cipher_line) == 0:
            continue
        i += 1
        print(f'{i}-', cipher_line)
        print(f'{i}+', decrypted_line)
        print('===================================')

plain_text = Path(DATA/"q21.txt").read_text()
cipher_text = Path(DATA/"q22.txt").read_text()
plain_count = count_alpha(plain_text)
cipher_count = count_alpha(cipher_text)
print(f"{plain_count=}\n{cipher_count=}\n")
# mapping = {}
# for ep, ec in zip(plain_count, cipher_count):
#     mapping[ec[0]] = ep[0]

mapping = {
  "t": "e", #
  "q": "a", #
  "z": "t", #
  "f": "n", #
  "o": "i", #
  "k": "r", #
  "g": "o", #
  "l": "s", #
  "i": "h", #
  "r": "d", #
  "e": "c", #
  "s": "l", #
  "x": "u", #
  "h": "p", #
  "d": "m", #
  "u": "g", #
  "y": "f", #
  "w": "b", #
  "c": "v", #
  "v": "w", #
  "b": "x", #
  "n": "y", #
  "a": "k", #
  "j": "q", #
  "m": "z", #
  "p": "j", #
}

# print(json.dumps(mapping, indent=2))

decrypted_text = translate(cipher_text, mapping)
line_1 = decrypted_text.split('\n')[:10]
# print(cipher_text[:1000])
# print("---------------")
# print(decrypted_text[:1000])

compare(cipher_text[:5000], decrypted_text[:5000])
Path(OUTPUT/"a22.txt").write_text(decrypted_text)