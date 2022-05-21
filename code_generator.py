from functools import reduce
import math


class CodeGenerator:

    def __init__(self, megahertz, repeat_register):
        self._register = repeat_register
        self._cycles_per_microsecond = megahertz
        self._code = []
        self._ports = {
            # TODO: 0x3e is actually SPH - we need PORTA or something
            'h_sync': ('0x03', 1),
            'v_sync': ('0x03', 1),
            'picture': ('0x03', 1),
        }
        self._opcodes = {
            'brne': 1,  # ... or 2 when it loops!
            'cbi': 2,
            'dec': 1,
            'jmp': 3,
            'ldi': 1,
            'rjmp': 2,
            'sbi': 2,
        }

    def start(self):
        self._code = []
        return self

    def label(self, label):
        self._code.append(f'{label}:')
        return self

    def delay_will_be_here(self):
        return self.label(':DELAY')

    def toggle(self, line, state):
        (port, bit) = self._ports[line]
        self._code.append(('sbi' if state else 'cbi') + f' {port}, {bit}')
        return self

    def next_line_count(self, repeats):
        self._code.append(f'ldi {self._register}, {repeats}')
        return self

    def loop(self, label):
        self._code.extend([f'dec {self._register}', f'brne {label}'])
        return self

    def goto(self, label):
        self._code.append(f'rjmp {label}')
        return self

    def _is_label(self, instruction):
        return instruction[-1] == ':'

    def _used_cycles(self, cycles, instruction):
        '''subtract an instruction's number of cycles from a running count'''
        if self._is_label(instruction):
            return cycles
        opcode = instruction.split(maxsplit=1)[0];
        return cycles - self._opcodes[opcode]

    def padding_cycles(self, required_microseconds):
        '''return the remaining number of cycles from the required'''
        return reduce(
            self._used_cycles,
            self._code,
            math.floor(required_microseconds * self._cycles_per_microsecond)
        )

    def code(self):
        return self._code

    def insert_delay(self, code):
        '''insert a delay at the designated point or at the end of this block'''
        if ':DELAY:' in self._code:
            pos = self._code.index(':DELAY:')
            self._code.remove(':DELAY:')
            for instruction in reversed(code):
                self._code.insert(pos, instruction)
        else:
            self._code.extend(code)
        return self
