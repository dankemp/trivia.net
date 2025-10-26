"""
Question generation and solving functions for Trivia.NET

This module contains:
1. Generation functions: Create random questions
2. Solving functions: Get the correct answer for a question

Both server and client import from this module.
"""

import random
import ipaddress
import ast
import operator


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
    allowed_ops = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,  # unary minus
        ast.UAdd: operator.pos  # unary plus
    }

    def _eval(node):
        if isinstance(node, ast.Num):  # <number>
            return node.n
        elif isinstance(node, ast.BinOp):  # <left> <op> <right>
            if type(node.op) in allowed_ops:
                return allowed_ops[type(node.op)](_eval(node.left), _eval(node.right))
        elif isinstance(node, ast.UnaryOp):  # + or - before a number
            if type(node.op) in allowed_ops:
                return allowed_ops[type(node.op)](_eval(node.operand))
        raise ValueError("Unsupported expression")

    parsed = ast.parse(expression, mode='eval')
    result = _eval(parsed.body)
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

def generate_usable_ip_addresses_question():
    """
    Generate a random subnet in CIDR notation.
    Returns a string like "192.168.1.0/24".
    """
    # Generate random IP and prefix length
    octets = [random.randint(0, 255) for _ in range(4)]
    ip = '.'.join(map(str, octets))
    prefix_length = random.randint(8, 30)  # /8 to /30

    return f"{ip}/{prefix_length}"


def solve_usable_ip_addresses_question(cidr):
    """
    Calculate number of usable IP addresses in a subnet.

    Args:
        cidr: String like "192.168.1.0/24"

    Returns:
        String representation of usable addresses (e.g., "254")
        Usable = Total - 2 (network and broadcast addresses)
    """
    network = ipaddress.IPv4Network(cidr, strict=False)
    # Usable addresses = total - 2 (network and broadcast)
    usable = network.num_addresses - 2
    return str(usable)


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
    network = ipaddress.IPv4Network(cidr, strict=False)
    network_addr = str(network.network_address)
    broadcast_addr = str(network.broadcast_address)
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
        "Usable IP Addresses of a Subnet": generate_usable_ip_addresses_question,
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