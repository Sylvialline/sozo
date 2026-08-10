from collections import defaultdict, Counter
from itertools import batched
import math
from pathlib import Path
import sys
from typing import Iterable
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from utils import Case, Exam, Input, read_data as rd


exam = Exam(reader=rd)

@exam.task(
    Case(
        "test",
        {"left": Input("1"), "right": [Input("1"), Input("2")]}
    )
)
def task_test(data):
    print(data)
    return data

if __name__ == "__main__":
    exam.execute()