class AvrDelay:

    def __init__(self, register):
        self._register = register
        self._label_count = 0

    def _label(self):
        self._label_count = self._label_count + 1
        return f'delay{self._label_count}'

    def _remainder(self, cycles):
        if cycles == 2:
            return ['rjmp PC+1']
        if cycles == 1:
            return ['nop']
        return []

    def _nine_or_more(self, cycles):
        count = cycles // 3
        if count == 256:
            count = 0
        label = self._label()
        result = [
            f'ldi {self._register}, {count}',
            f'{label}:',
            f'dec {self._register}',
            f'brne {label}'
        ]
        return result + self._remainder(cycles % 3)

    def _under_nine(self, cycles):
        if cycles == 4:
            return ['rjmp PC+1'] * 2
        result = [f'lpm {self._register}, Z'] * (cycles // 3)
        return result + self._remainder(cycles % 3)

    def delay_loop(self, cycles):
        if cycles < 0:
            raise ValueError(
                'cycles < 0 - time machine not found!'
            )
        max_size = 256 * 3
        if cycles > max_size:
            raise ValueError(
                f'cycles > {max_size} - TODO: implement nested loops'
            )
        if cycles == 0:
            return []
        if cycles < 9:
            return self._under_nine(cycles)
        return self._nine_or_more(cycles)
