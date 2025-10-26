#!/usr/bin/env python3
"""
Tests for error handling in server and client

Tests various error scenarios and edge cases.
"""

import unittest
import subprocess
import os
import json
import time


class TestServerErrorHandling(unittest.TestCase):
    """Test server error handling"""

    def test_server_missing_config_arg(self):
        """Test server with missing --config argument"""
        result = subprocess.run(
            ['python3', 'server.py'],
            capture_output=True,
            text=True,
            timeout=2
        )

        # Should exit with code 1
        self.assertEqual(result.returncode, 1)

        # Should print error to stderr
        self.assertIn('Configuration not provided', result.stderr)

    def test_server_nonexistent_config_file(self):
        """Test server with non-existent config file"""
        result = subprocess.run(
            ['python3', 'server.py', '--config', 'nonexistent_file.json'],
            capture_output=True,
            text=True,
            timeout=2
        )

        # Should exit with code 1
        self.assertEqual(result.returncode, 1)

        # Should print error to stderr
        self.assertIn('does not exist', result.stderr)
        self.assertIn('nonexistent_file.json', result.stderr)

    def test_server_port_in_use(self):
        """Test server when port is already in use"""
        # Create a test config
        os.makedirs("tests/configs", exist_ok=True)
        config_path = "tests/configs/port_test.json"

        config = {
            "port": 11111,
            "players": 1,
            "question_types": ["Mathematics"],
            "question_formats": {"Mathematics": "What is {}?"},
            "question_seconds": 5,
            "question_interval_seconds": 1,
            "ready_info": "Starting!",
            "question_word": "Q",
            "correct_answer": "Right!",
            "incorrect_answer": "Wrong!",
            "points_noun_singular": "point",
            "points_noun_plural": "points",
            "final_standings_heading": "Final:",
            "one_winner": "Winner: {}",
            "multiple_winners": "Winners: {}"
        }

        with open(config_path, 'w') as f:
            json.dump(config, f)

        # Start first server
        server1 = subprocess.Popen(
            ['python3', 'server.py', '--config', config_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        try:
            time.sleep(0.5)

            # Try to start second server on same port
            result = subprocess.run(
                ['python3', 'server.py', '--config', config_path],
                capture_output=True,
                text=True,
                timeout=2
            )

            # Second server should fail
            self.assertEqual(result.returncode, 1)
            self.assertIn('Binding to port', result.stderr)
            self.assertIn('unsuccessful', result.stderr)

        finally:
            server1.terminate()
            server1.wait(timeout=2)


class TestClientErrorHandling(unittest.TestCase):
    """Test client error handling"""

    def test_client_missing_config_arg(self):
        """Test client with missing --config argument"""
        result = subprocess.run(
            ['python3', 'client.py'],
            capture_output=True,
            text=True,
            timeout=2,
            input='\n'  # Provide empty input
        )

        # Should exit with code 1
        self.assertEqual(result.returncode, 1)

        # Should print error to stderr
        self.assertIn('Configuration not provided', result.stderr)

    def test_client_nonexistent_config_file(self):
        """Test client with non-existent config file"""
        result = subprocess.run(
            ['python3', 'client.py', '--config', 'nonexistent_client.json'],
            capture_output=True,
            text=True,
            timeout=2,
            input='\n'
        )

        # Should exit with code 1
        self.assertEqual(result.returncode, 1)

        # Should print error to stderr
        self.assertIn('does not exist', result.stderr)
        self.assertIn('nonexistent_client.json', result.stderr)

    def test_client_missing_ollama_config_in_ai_mode(self):
        """Test client in AI mode without ollama_config"""
        os.makedirs("tests/configs", exist_ok=True)
        config_path = "tests/configs/ai_missing_ollama.json"

        # Create config with ai mode but no ollama_config
        config = {
            "username": "AIPlayer",
            "client_mode": "ai"
            # Missing ollama_config
        }

        with open(config_path, 'w') as f:
            json.dump(config, f)

        result = subprocess.run(
            ['python3', 'client.py', '--config', config_path],
            capture_output=True,
            text=True,
            timeout=2,
            input='\n'
        )

        # Should exit with code 1
        self.assertEqual(result.returncode, 1)

        # Should print error about missing Ollama config
        self.assertIn('Ollama', result.stderr)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""

    def test_question_with_negative_result(self):
        """Test mathematics question with negative result"""
        from questions import solve_mathematics_question

        result = solve_mathematics_question("5 - 10")
        self.assertEqual(result, "-5")

        result = solve_mathematics_question("1 - 100")
        self.assertEqual(result, "-99")

    def test_smallest_roman_numeral(self):
        """Test smallest valid Roman numeral"""
        from questions import solve_roman_numerals_question

        result = solve_roman_numerals_question("I")
        self.assertEqual(result, "1")

    def test_largest_roman_numeral(self):
        """Test largest valid Roman numeral"""
        from questions import solve_roman_numerals_question

        result = solve_roman_numerals_question("MMMCMXCIX")
        self.assertEqual(result, "3999")

    def test_small_subnet(self):
        """Test very small subnet (/30)"""
        from questions import solve_usable_ip_addresses_question

        # /30 has 4 addresses, 2 usable
        result = solve_usable_ip_addresses_question("192.168.1.0/30")
        self.assertEqual(result, "2")

    def test_large_subnet(self):
        """Test large subnet (/8)"""
        from questions import solve_usable_ip_addresses_question

        # /8 has 2^24 = 16777216 addresses, minus 2 = 16777214 usable
        result = solve_usable_ip_addresses_question("10.0.0.0/8")
        self.assertEqual(result, "16777214")


if __name__ == '__main__':
    unittest.main(verbosity=2)
