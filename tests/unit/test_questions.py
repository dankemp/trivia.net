#!/usr/bin/env python3
"""
Unit tests for questions.py module

Tests question generation and solving functions.
"""

import unittest
import sys
import os

# Add parent directory to path to import questions
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from questions import *


class TestMathematicsQuestions(unittest.TestCase):
    """Test mathematics question generation and solving"""

    def test_generate_format(self):
        """Test that generated questions have correct format"""
        question = generate_mathematics_question()

        # Should contain numbers, +, -, and spaces
        self.assertTrue(all(c.isdigit() or c in ' +-' for c in question))

        # Should have at least 3 tokens (num op num)
        tokens = question.split()
        self.assertGreaterEqual(len(tokens), 3)

        # Should have odd number of tokens (num op num op num...)
        self.assertEqual(len(tokens) % 2, 1)

    def test_solve_simple_addition(self):
        """Test solving simple addition"""
        self.assertEqual(solve_mathematics_question("5 + 3"), "8")
        self.assertEqual(solve_mathematics_question("100 + 1"), "101")
        self.assertEqual(solve_mathematics_question("1 + 1"), "2")

    def test_solve_simple_subtraction(self):
        """Test solving simple subtraction"""
        self.assertEqual(solve_mathematics_question("10 - 4"), "6")
        self.assertEqual(solve_mathematics_question("50 - 25"), "25")
        self.assertEqual(solve_mathematics_question("5 - 10"), "-5")

    def test_solve_mixed_operations(self):
        """Test solving mixed + and - operations"""
        self.assertEqual(solve_mathematics_question("5 + 3 - 2"), "6")
        self.assertEqual(solve_mathematics_question("10 - 5 + 3 - 1"), "7")
        self.assertEqual(solve_mathematics_question("100 - 50 + 25 - 10 + 5"), "70")

    def test_solve_generated_questions(self):
        """Test that we can solve our own generated questions"""
        for _ in range(10):
            question = generate_mathematics_question()
            answer = solve_mathematics_question(question)

            # Answer should be a valid integer string (possibly negative)
            try:
                int(answer)
            except ValueError:
                self.fail(f"Invalid answer '{answer}' for question '{question}'")


class TestRomanNumeralsQuestions(unittest.TestCase):
    """Test Roman numerals question generation and solving"""

    def test_solve_simple(self):
        """Test solving simple Roman numerals"""
        self.assertEqual(solve_roman_numerals_question("I"), "1")
        self.assertEqual(solve_roman_numerals_question("V"), "5")
        self.assertEqual(solve_roman_numerals_question("X"), "10")
        self.assertEqual(solve_roman_numerals_question("L"), "50")
        self.assertEqual(solve_roman_numerals_question("C"), "100")
        self.assertEqual(solve_roman_numerals_question("D"), "500")
        self.assertEqual(solve_roman_numerals_question("M"), "1000")

    def test_solve_subtractive(self):
        """Test solving Roman numerals with subtractive notation"""
        self.assertEqual(solve_roman_numerals_question("IV"), "4")
        self.assertEqual(solve_roman_numerals_question("IX"), "9")
        self.assertEqual(solve_roman_numerals_question("XL"), "40")
        self.assertEqual(solve_roman_numerals_question("XC"), "90")
        self.assertEqual(solve_roman_numerals_question("CD"), "400")
        self.assertEqual(solve_roman_numerals_question("CM"), "900")

    def test_solve_complex(self):
        """Test solving complex Roman numerals"""
        self.assertEqual(solve_roman_numerals_question("XIV"), "14")
        self.assertEqual(solve_roman_numerals_question("XLII"), "42")
        self.assertEqual(solve_roman_numerals_question("MCMXCIV"), "1994")
        self.assertEqual(solve_roman_numerals_question("MMXXV"), "2025")

    def test_solve_edge_cases(self):
        """Test edge cases (min and max)"""
        self.assertEqual(solve_roman_numerals_question("I"), "1")
        self.assertEqual(solve_roman_numerals_question("MMMCMXCIX"), "3999")

    def test_generate_format(self):
        """Test that generated Roman numerals are valid"""
        valid_chars = set('IVXLCDM')

        for _ in range(10):
            roman = generate_roman_numerals_question()

            # Should only contain valid Roman numeral characters
            self.assertTrue(all(c in valid_chars for c in roman))

            # Should be non-empty
            self.assertGreater(len(roman), 0)

            # Should be solvable
            decimal = solve_roman_numerals_question(roman)
            value = int(decimal)
            self.assertGreaterEqual(value, 1)
            self.assertLessEqual(value, 3999)


class TestIPAddressQuestions(unittest.TestCase):
    """Test IP address question generation and solving"""

    def test_solve_usable_addresses(self):
        """Test calculating usable IP addresses"""
        # /24 = 256 total - 2 = 254 usable
        self.assertEqual(solve_usable_ip_addresses_question("192.168.1.0/24"), "254")

        # /25 = 128 total - 2 = 126 usable
        self.assertEqual(solve_usable_ip_addresses_question("10.0.0.0/25"), "126")

        # /30 = 4 total - 2 = 2 usable
        self.assertEqual(solve_usable_ip_addresses_question("172.16.0.0/30"), "2")

        # /16 = 65536 total - 2 = 65534 usable
        self.assertEqual(solve_usable_ip_addresses_question("10.0.0.0/16"), "65534")

    def test_solve_network_broadcast(self):
        """Test calculating network and broadcast addresses"""
        result = solve_network_broadcast_question("192.168.1.37/24")
        self.assertEqual(result, "192.168.1.0 and 192.168.1.255")

        result = solve_network_broadcast_question("10.20.30.40/16")
        self.assertEqual(result, "10.20.0.0 and 10.20.255.255")

        result = solve_network_broadcast_question("172.16.5.10/20")
        self.assertEqual(result, "172.16.0.0 and 172.16.15.255")

    def test_generate_usable_addresses_format(self):
        """Test that generated questions are valid CIDR notation"""
        for _ in range(10):
            cidr = generate_usable_ip_addresses_question()

            # Should contain /
            self.assertIn('/', cidr)

            # Should have IP and prefix
            ip, prefix = cidr.split('/')

            # IP should have 4 octets
            octets = ip.split('.')
            self.assertEqual(len(octets), 4)

            # Prefix should be valid
            prefix_int = int(prefix)
            self.assertGreaterEqual(prefix_int, 8)
            self.assertLessEqual(prefix_int, 30)

            # Should be solvable
            answer = solve_usable_ip_addresses_question(cidr)
            int(answer)  # Should not raise exception

    def test_generate_network_broadcast_format(self):
        """Test that network/broadcast questions are valid"""
        for _ in range(10):
            cidr = generate_network_broadcast_question()

            # Should be valid CIDR
            self.assertIn('/', cidr)

            # Should be solvable
            answer = solve_network_broadcast_question(cidr)
            self.assertIn(' and ', answer)

            network, broadcast = answer.split(' and ')

            # Both should be valid IPs
            self.assertEqual(len(network.split('.')), 4)
            self.assertEqual(len(broadcast.split('.')), 4)


class TestHelperFunctions(unittest.TestCase):
    """Test helper functions"""

    def test_get_generator(self):
        """Test get_generator returns correct functions"""
        self.assertEqual(
            get_generator("Mathematics"),
            generate_mathematics_question
        )
        self.assertEqual(
            get_generator("Roman Numerals"),
            generate_roman_numerals_question
        )

    def test_get_solver(self):
        """Test get_solver returns correct functions"""
        self.assertEqual(
            get_solver("Mathematics"),
            solve_mathematics_question
        )
        self.assertEqual(
            get_solver("Roman Numerals"),
            solve_roman_numerals_question
        )


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
