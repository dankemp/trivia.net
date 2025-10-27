"""
Question generation and solving functions for Trivia.NET

This module contains:
1. Generation functions: Create random questions
2. Solving functions: Get the correct answer for a question

Both server and client import from this module.
"""

import random


# ============================================================================
# IP ADDRESS HELPER FUNCTIONS
# ============================================================================

def ip_to_int(ip_str):
    """Convert IP address string to 32-bit integer."""
    octets = ip_str.split('.')
    return (int(octets[0]) << 24) + (int(octets[1]) << 16) + \
           (int(octets[2]) << 8) + int(octets[3])


def int_to_ip(ip_int):
    """Convert 32-bit integer to IP address string."""
    return f"{(ip_int >> 24) & 0xFF}.{(ip_int >> 16) & 0xFF}." \
           f"{(ip_int >> 8) & 0xFF}.{ip_int & 0xFF}"


def parse_cidr(cidr):
    """
    Parse CIDR notation and return network address, broadcast address, and host count.

    Args:
        cidr: String like "192.168.1.37/24"

    Returns:
        Tuple of (network_addr_str, broadcast_addr_str, num_addresses)
    """
    #print("cidr tttttttttt: " + cidr)
    try:
        ip_str, prefix_str = cidr.split('/')
    except ValueError:
        print("Invalid cidr: " + cidr)
        return
    prefix_length = int(prefix_str)

    # Convert IP to integer
    ip_int = ip_to_int(ip_str)

    # Calculate subnet mask
    # For /24: 11111111.11111111.11111111.00000000 = 0xFFFFFF00
    mask = (0xFFFFFFFF << (32 - prefix_length)) & 0xFFFFFFFF

    # Calculate network address (IP AND mask)
    network_int = ip_int & mask

    # Calculate broadcast address (network OR inverted mask)
    broadcast_int = network_int | (~mask & 0xFFFFFFFF)

    # Total number of addresses in subnet
    num_addresses = 2 ** (32 - prefix_length)

    return (int_to_ip(network_int), int_to_ip(broadcast_int), num_addresses)


# ============================================================================
# MATHEMATICS QUESTIONS
# ============================================================================

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
    """
    Solve a mathematics expression.

    Args:
        expression: String like "5 + 3 - 2"

    Returns:
        String representation of the result (e.g., "6")
    """
    # Parse and evaluate without using eval()
    # Since we only have + and - operators (no precedence), evaluate left-to-right
    tokens = expression.split()

    # Start with first number
    result = int(tokens[0])

    # Process operators and operands
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


# ============================================================================
# ROMAN NUMERALS QUESTIONS
# ============================================================================

def generate_roman_numerals_question():
    """
    Generate a random Roman numeral from 1-3999.
    Returns the Roman numeral as a string (e.g., "MCMXCIV").
    """
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
    """
    Convert Roman numeral to decimal.

    Args:
        roman: String like "XIV" or "MCMXCIV"

    Returns:
        String representation of decimal value (e.g., "14" or "1994")
    """
    values = {
        'I': 1, 'V': 5, 'X': 10, 'L': 50,
        'C': 100, 'D': 500, 'M': 1000
    }

    total = 0
    prev_value = 0

    # Process right to left
    for char in reversed(roman):
        if char not in values:
            continue
        value = values[char]
        if value < prev_value:
            # Subtractive notation (like IV = 4)
            total -= value
        else:
            total += value
        prev_value = value

    return str(total)


# ============================================================================
# USABLE IP ADDRESSES QUESTIONS
# ============================================================================

def generate_usable_addresses_question():
    """
    Generate a random subnet in CIDR notation.
    Returns a string like "192.168.1.0/24".
    """
    # Generate random IP and prefix length
    octets = [random.randint(0, 255) for _ in range(4)]
    ip = '.'.join(map(str, octets))
    prefix_length = random.randint(8, 30)  # /8 to /30

    return f"{ip}/{prefix_length}"


# Alias for Ed compatibility
#generate_usable_addresses_question = generate_usable_ip_addresses_question


def solve_usable_ip_addresses_question(cidr):
    """
    Calculate number of usable IP addresses in a subnet.

    Args:
        cidr: String like "192.168.1.0/24"

    Returns:
        String representation of usable addresses (e.g., "254")
        Usable = Total - 2 (network and broadcast addresses)
    """
    _, _, num_addresses = parse_cidr(cidr)
    # Usable addresses = total - 2 (network and broadcast)
    usable = num_addresses - 2
    return str(usable)


# Alias for Ed compatibility
solve_usable_addresses_question = solve_usable_ip_addresses_question


# ============================================================================
# NETWORK AND BROADCAST ADDRESS QUESTIONS
# ============================================================================

def generate_network_broadcast_question():
    """
    Generate a random subnet for network/broadcast calculation.
    Returns a string like "192.168.1.37/24".
    """
    octets = [random.randint(0, 255) for _ in range(4)]
    ip = '.'.join(map(str, octets))
    prefix_length = random.randint(8, 30)

    return f"{ip}/{prefix_length}"


def solve_network_broadcast_question(cidr):
    """
    Calculate network and broadcast addresses of a subnet.

    Args:
        cidr: String like "192.168.1.37/24"

    Returns:
        String in format "network_addr and broadcast_addr"
        (e.g., "192.168.1.0 and 192.168.1.255")
    """
    network_addr, broadcast_addr, _ = parse_cidr(cidr)
    return f"{network_addr} and {broadcast_addr}"


# ============================================================================
# CONVENIENCE FUNCTIONS (Optional)
# ============================================================================

def get_generator(question_type: str):
    """
    Get the generator function for a given question type.

    Args:
        question_type: One of the question type strings

    Returns:
        The generator function
    """
    generators = {
        "Mathematics": generate_mathematics_question,
        "Roman Numerals": generate_roman_numerals_question,
        "Usable IP Addresses of a Subnet": generate_usable_addresses_question,
        "Network and Broadcast Address of a Subnet": generate_network_broadcast_question
    }
    return generators[question_type]


def get_solver(question_type: str):
    """
    Get the solver function for a given question type.

    Args:
        question_type: One of the question type strings

    Returns:
        The solver function
    """
    solvers = {
        "Mathematics": solve_mathematics_question,
        "Roman Numerals": solve_roman_numerals_question,
        "Usable IP Addresses of a Subnet": solve_usable_ip_addresses_question,
        "Network and Broadcast Address of a Subnet": solve_network_broadcast_question
    }
    return solvers[question_type]