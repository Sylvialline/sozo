from enum import Enum, auto
from pathlib import Path
import sys
from typing import Optional

HERE, ROOT = Path(__file__).resolve().parents[:2]
sys.path.insert(0, str(ROOT))
DATA = HERE / "data"
# OUTPUT = HERE / "output"
# OUTPUT.mkdir(exist_ok=True)

from utils import Case, Exam

class Opcode(Enum):
    ADD = auto()
    CMP = auto()
    JMP = auto()
    PRN = auto()
    SET = auto()
    SUB = auto()
    BAK = auto()
    CAL = auto()
    RET = auto()

Inst = tuple[Opcode, str, str]

Program = list[Inst]

def load_program(filename: str) -> Program:
    p = []
    with (DATA/filename).open() as f:
        for line in f:
            opcode, a, b = line.split()
            p.append((Opcode[opcode], a, b))
    return p


exam = Exam(reader=load_program)

class SubReturn(Exception):
    pass

class CallReturn(Exception):
    pass

class Printed(Exception):
    pass

class Runtime:

    def __init__(self, program: Program, pc: int = 0, names: Optional[dict[str, int]] = None) -> None:
        self.program = program
        self.pc = pc
        self.names = {} if names is None else names

    def value(self, name: str):
        try:
            return int(name)
        except ValueError:
            return self.names.get(name, 0)

    def __setitem__(self, name: str, value: int):
        self.names[name] = value

    def _next(self):
        op, a, b = self.program[self.pc]
        av = self.value(a)
        bv = self.value(b)
        self.pc += 1
        match op:
            case Opcode.ADD:
                self[b] = av + bv
            case Opcode.CMP:
                if av == bv:
                    self.pc += 1
            case Opcode.JMP:
                self.pc += av - 1
            case Opcode.PRN:
                raise Printed(av, bv)
            case Opcode.SET:
                self[a] = bv
            case Opcode.SUB:
                subpc = self.pc + av - 1
                Sub(self.program, subpc, self.names).run()
            case Opcode.BAK:
                raise SubReturn
            case Opcode.CAL:
                funcpc = self.pc + av - 1
                funcnames = {'in': bv}
                self["out"] = Func(self.program, funcpc, funcnames).run()
            case Opcode.RET:
                raise CallReturn(av)


    def run(self):
        raise NotImplementedError

class Sub(Runtime):
    def run(self):
        while True:
            try:
                self._next()
            except SubReturn:
                return

class Func(Runtime):
    def run(self):
        while True:
            try:
                self._next()
            except CallReturn as e:
                return e.args[0]

class Main(Runtime):
    def run(self):
        while True:
            try:
                self._next()
            except Printed as e:
                return e.args

@exam.task(
    Case("1", files=("prog1.txt",))
)
def task1(p: Program):
    return [a for op, a, b in p]

@exam.task(
    Case("3", files=("prog2.txt",)),
    Case("4", files=("prog3.txt",)),
    Case("5", files=("prog4.txt",)),
    Case("6", files=("prog5.txt",)),
)
def task_run(p: Program):
    return Main(p).run()

exam.execute()

