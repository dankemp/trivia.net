"""
Question generation and solving functions for Trivia.NET

This module contains:
1. Generation functions: Create random questions
2. Solving functions: Get the correct answer for a question

Both server and client import from this module.
"""

import random

def ip_to_int(ip_str):
    octets = ip_str.split('.')
    return (int(octets[0]) << 24) + (int(octets[1]) << 16) + \
           (int(octets[2]) << 8) + int(octets[3])


def int_to_ip(ip_int):
    return f"{(ip_int >> 24) & 0xFF}.{(ip_int >> 16) & 0xFF}." \
           f"{(ip_int >> 8) & 0xFF}.{ip_int & 0xFF}"


def parse_cidr(cidr):

    try:
        ip_str, prefix_str = cidr.split('/')
    except ValueError:
        print("Invalid cidr: " + cidr)
        return
    prefix_length = int(prefix_str)

    ip_int = ip_to_int(ip_str)

    mask = (0xFFFFFFFF << (32 - prefix_length)) & 0xFFFFFFFF

    network_int = ip_int & mask

    broadcast_int = network_int | (~mask & 0xFFFFFFFF)

    num_addresses = 2 ** (32 - prefix_length)

    return (int_to_ip(network_int), int_to_ip(broadcast_int), num_addresses)



def generate_mathematics_question():
    """
    Generate a random mathematics expression with 2-5 operands and +/- operators.
    Returns the expression as a string (e.g., "5 + 3 - 2").
    """
    num_operands = random.randint(2, 5)
    operands = [random.randint(1, 100) for _ in range(num_operands)]
    operators = [random.choice(['+', '-']) for _ in range(num_operands - 1)]

    # Build expression string
    expression = str(operands[0])
    for i, op in enumerate(operators):
        expression += f" {op} {operands[i + 1]}"

    return expression


def solve_mathematics_question(expression):

    tokens = expression.split()

    result = int(tokens[0])

    i = 1
    while i < len(tokens):
        operator = tokens[i]
        operand = int(tokens[i + 1])

        if operator == '+':
            result += operand
        elif operator == '-':
            result -= operand

        i += 2

    return str(result)


def generate_roman_numerals_question():

    number = random.randint(1, 3999)

    # Convert to Roman numeral
    values = [
        (1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'),
        (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'),
        (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')
    ]

    roman = ''
    for value, numeral in values:
        count = number // value
        roman += numeral * count
        number -= value * count

    return roman


def solve_roman_numerals_question(roman):

    val = {
        'I': 1, 'V': 5, 'X': 10, 'L': 50,
        'C': 100, 'D': 500, 'M': 1000
    }

    total = 0
    prev_value = 0

    # right to left
    for char in reversed(roman):
        if char not in val:
            continue
        value = val[char]
        if value < prev_value:
            # Subtractive
            total -= value
        else:
            total += value
        prev_value = value

    return str(total)

def generate_usable_addresses_question():

    octets = [random.randint(0, 255) for _ in range(4)]
    ip = '.'.join(map(str, octets))
    prefix_length = random.randint(0, 32)  # /0 to /32

    return f"{ip}/{prefix_length}"

def solve_usable_addresses_question(cidr):

    _, _, num_addresses = parse_cidr(cidr)
    if num_addresses == 1:
        usable = 1
    elif num_addresses == 2:
        usable = 2
    else:
        usable = num_addresses - 2
    return str(usable)



def generate_network_broadcast_question():

    octets = [random.randint(0, 255) for _ in range(4)]
    ip = '.'.join(map(str, octets))
    prefix_length = random.randint(0, 32)

    return f"{ip}/{prefix_length}"


def solve_network_broadcast_question(cidr):

    network_addr, broadcast_addr, _ = parse_cidr(cidr)
    return f"{network_addr} and {broadcast_addr}"


def get_generator(question_type: str):

    generators = {
        "Mathematics": generate_mathematics_question,
        "Roman Numerals": generate_roman_numerals_question,
        "Usable IP Addresses of a Subnet": generate_usable_addresses_question,
        "Network and Broadcast Address of a Subnet": generate_network_broadcast_question
    }
    return generators[question_type]


def get_solver(question_type: str):

    solvers = {
        "Mathematics": solve_mathematics_question,
        "Roman Numerals": solve_roman_numerals_question,
        "Usable IP Addresses of a Subnet": solve_usable_addresses_question,
        "Network and Broadcast Address of a Subnet": solve_network_broadcast_question
    }
    return solvers[question_type]