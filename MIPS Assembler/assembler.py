import re  # Import regular expressions module for splitting strings based on patterns

# Dictionary to map instruction mnemonics to their opcode and function codes
instruction_set = {
    'R': {  # R-type instructions
        'ADD':  '100000', 'SUB':  '100010', 'AND':  '100100', 'OR':   '100101',
        'SLL':  '000000', 'SRL':  '000010', 'SLLV': '000100', 'SRLV': '000110'
    },
    'I': {  # I-type instructions
        'ADDI': '001000', 'ANDI': '001100', 'LW':   '100011', 'SW':   '101011',
        'BEQ':  '000100', 'BNE':  '000101', 'BLEZ': '000110', 'BGTZ': '000111'
    },
    'J': {  # J-type instructions
        'J':    '000010'
    }
}

def parse_source_code(filename):
    """
    Parses the source code to extract labels and instructions with their addresses.
    """
    with open(filename, 'r') as file:
        lines = file.readlines()  # Read all lines from the file

    labels = {}  # Dictionary to store label addresses
    instructions = []  # List to store instructions with their addresses
    address = 0x00400000  # Starting address of the program

    for line in lines:
        # Remove comments and leading/trailing whitespace
        line = line.split('#')[0].strip()
        if not line:  # Skip empty lines
            continue

        # Check if the line contains a label
        if ':' in line:
            label = line.split(':')[0].strip()  # Extract the label name
            labels[label] = address  # Map label to the current address
            line = line.split(':')[1].strip()  # Get the remaining instruction part

        if line:  # If there's an instruction part left
            instructions.append((address, line))  # Add the instruction with its address
            address += 4  # Increment address by 4 (each instruction is 4 bytes)

    return labels, instructions  # Return the labels and instructions

def reg_to_bin(reg):
    """
    Converts a register name to a 5-bit binary string.
    """
    reg_num = int(reg[1:])  # Extract the register number (ignore the '$')
    return format(reg_num, '05b')  # Convert the number to a 5-bit binary string

def instruction_to_machine_code(instruction, labels, current_address):
    """
    Converts an instruction to its binary machine code representation.
    """
    parts = re.split(r'[,\s]\s*', instruction)  # Split the instruction into parts
    opcode, rest = parts[0], parts[1:]  # Separate the opcode and the rest of the instruction

    print(f"Processing instruction: {instruction}")
    print(f"Opcode: {opcode}, Rest: {rest}")

    if opcode.upper() in instruction_set['R']:
        # Handle R-type instructions
        rd = reg_to_bin(rest[0])  # Destination register
        rs = reg_to_bin(rest[1])  # Source register
        rt = reg_to_bin(rest[2])  # Target register
        shamt = format(int(rest[3]), '05b') if opcode.upper() in ['SLL', 'SRL'] else '00000'  # Shift amount
        funct = instruction_set['R'][opcode.upper()]  # Function code
        return '000000' + rs + rt + rd + shamt + funct  # Construct the machine code

    elif opcode.upper() in instruction_set['I']:
        # Handle I-type instructions
        rt = reg_to_bin(rest[0])  # Target register
        rs = reg_to_bin(rest[1])  # Source register
        if opcode.upper() in ['LW', 'SW']:
            offset = int(rest[2])  # Offset value
            return instruction_set['I'][opcode.upper()] + rs + rt + format(offset, '016b')  # Construct the machine code
        elif opcode.upper() in ['BEQ', 'BNE']:
            offset = (labels[rest[2]] - current_address - 4) >> 2  # Calculate branch offset
            return instruction_set['I'][opcode.upper()] + rs + rt + format(offset & 0xFFFF, '016b')  # Construct the machine code
        else:
            immediate = int(rest[2]) & 0xFFFF  # Immediate value
            return instruction_set['I'][opcode.upper()] + rs + rt + format(immediate, '016b')  # Construct the machine code

    elif opcode.upper() in instruction_set['J']:
        # Handle J-type instructions
        address = labels[rest[0]] >> 2  # Jump address
        return instruction_set['J'][opcode.upper()] + format(address, '026b')  # Construct the machine code

def assemble(filename):
    """
    Assembles the given MIPS assembly file into machine code and writes to a .obj file.
    """
    labels, instructions = parse_source_code(filename)  # Parse the source code
    output_filename = filename.replace('.asm', '.obj')  # Create output filename with .obj extension
    with open(output_filename, 'w') as output_file:
        for address, instruction in instructions:
            machine_code = instruction_to_machine_code(instruction, labels, address)  # Convert to machine code
            output_file.write(f'{format(address, "08X")}: {machine_code}\n')  # Write address and machine code to file


if __name__ == "__main__":
    assemble(r'C:\Users\ahmet\PycharmProjects\MIPS Assembler\example.asm')
