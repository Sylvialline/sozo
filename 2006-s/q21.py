from collections import Counter
from pathlib import Path
HERE, ROOT = Path(__file__).resolve().parents[:2]
DATA = HERE/"data"

def count_alpha(text: str):
    counter = Counter(text.lower())
    return [(char, cnt) for char, cnt in counter.most_common() if char.isalpha()]

text = Path(DATA/"q21.txt").read_text()

if __name__ == "__main__":

    print(count_alpha(text))
    for char, cnt in count_alpha(text):
        if char.isalpha():
            print(char, cnt)