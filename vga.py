from code_generator import CodeGenerator
from avr_delay import AvrDelay

calculate = AvrDelay('r16')
generator = CodeGenerator(15, 'r17')

assembler = []

# timings for SVGA 800x600 @ 60Hz
microseconds = {
    'visible': 20,
    'front': 1,
    'sync': 3.2,
    'back': 2.2
}
lines = {
    'visible_div_3': 200,
    'front': 1,
    'sync': 4,
    'back': 23
}

def code(cycles):
    if cycles > 0:
        generator.insert_delay(calculate.delay_loop(cycles))
    assembler.extend(generator.code())


assembler.extend(
    generator.start()
    .label('todo_port_setup')
    .toggle('v_sync', False)
    .toggle('h_sync', False)
    .next_line_count(lines['visible_div_3'])
    .code()
)

# the normal lines
for block in range(1, 3):
    label = f'normal{block}'
    code(
        generator.start()
        .label(label)
        .toggle('picture', True)
        .padding_cycles(microseconds['visible'])
    )
    code(
        generator.start()
        .toggle('picture', False)
        .padding_cycles(microseconds['front'])
    )
    code(
        generator.start()
        .toggle('h_sync', True)
        .padding_cycles(microseconds['sync'])
    )
    code(
        generator.start()
        .toggle('h_sync', False)
        .delay_will_be_here()
        .loop(label)
        .next_line_count(lines['visible_div_3'])
        .padding_cycles(microseconds['back'])
    )

# Vertical front porch - no count here because there's only 1 line
code(
    generator.start()
    .label('f_porch')
    .toggle('picture', False)
    .padding_cycles(microseconds['visible'] + microseconds['front'])
)
code(
    generator.start()
    .toggle('h_sync', True)
    .padding_cycles(microseconds['sync'])
)
code(
    generator.start()
    .toggle('h_sync', False)
    .delay_will_be_here()
    .next_line_count(lines['sync'])
    .padding_cycles(microseconds['back'])
)

# vertical sync
code(
    generator.start()
    .label('v_synch')
    .toggle('v_sync', True)
    .padding_cycles(microseconds['visible'] + microseconds['front'])
)
code(
    generator.start()
    .toggle('h_sync', True)
    .padding_cycles(microseconds['sync'])
)
code(
    generator.start()
    .toggle('h_sync', False)
    .delay_will_be_here()
    .loop('v_synch')
    .next_line_count(lines['back'])
    .padding_cycles(microseconds['back'])
)

#vertical back porch
code(
    generator.start()
    .label('b_porch')
    .toggle('v_sync', False)
    .padding_cycles(microseconds['visible'] + microseconds['front'])
)
code(
    generator.start()
    .toggle('h_sync', True)
    .padding_cycles(microseconds['sync'])
)
code(
    generator.start()
    .toggle('h_sync', False)
    .delay_will_be_here()
    .loop('b_porch')
    # we have one extra normal line at the bottom
    # to fix timing issues with the final RJMP
    .next_line_count(lines['visible_div_3'] - 1)
    .padding_cycles(microseconds['back'])
)

code(
    generator.start()
    .label('extra_line')
    .toggle('picture', True)
    .padding_cycles(microseconds['visible'])
)
code(
    generator.start()
    .toggle('picture', False)
    .padding_cycles(microseconds['front'])
)
code(
    generator.start()
    .toggle('h_sync', True)
    .padding_cycles(microseconds['sync'])
)
code(
    generator.start()
    .toggle('h_sync', False)
    .delay_will_be_here()
    .goto('normal1')
    .padding_cycles(microseconds['back'])
)

print("\n".join(assembler))
