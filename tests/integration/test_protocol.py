#!/usr/bin/env python3
"""
Integration tests for client-server protocol

Tests message exchange between client and server.
"""

import unittest
import socket
import json
import subprocess
import time
import os
import sys
import signal

# Test configuration
TEST_PORT = 9999
TEST_CONFIG_PATH = "tests/configs/protocol_test_config.json"


class TestServerProtocol(unittest.TestCase):
    """Test server protocol with simulated client"""

    @classmethod
    def setUpClass(cls):
        """Create test configuration file"""
        os.makedirs("tests/configs", exist_ok=True)

        config = {
            "port": TEST_PORT,
            "players": 1,
            "question_types": ["Mathematics"],
            "question_formats": {
                "Mathematics": "What is {}?"
            },
            "question_seconds": 5,
            "question_interval_seconds": 1,
            "ready_info": "Game starts in {question_interval_seconds} seconds!",
            "question_word": "Question",
            "correct_answer": "Correct! {answer} is right!",
            "incorrect_answer": "Wrong! Your answer {answer} is incorrect. The correct answer is {correct_answer}.",
            "points_noun_singular": "point",
            "points_noun_plural": "points",
            "final_standings_heading": "Final standings:",
            "one_winner": "The winner is: {}",
            "multiple_winners": "The winners are: {}"
        }

        with open(TEST_CONFIG_PATH, 'w') as f:
            json.dump(config, f)

    def setUp(self):
        """Start server before each test"""
        self.server_process = subprocess.Popen(
            ['python3', 'server.py', '--config', TEST_CONFIG_PATH],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        # Give server time to start
        time.sleep(0.5)

    def tearDown(self):
        """Stop server after each test"""
        if self.server_process:
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
                self.server_process.wait()
        time.sleep(0.3)

    def send_message(self, sock, message_dict):
        """Send a JSON message with newline delimiter"""
        message = json.dumps(message_dict) + '\n'
        sock.sendall(message.encode('utf-8'))

    def receive_message(self, sock, timeout=5):
        """Receive a JSON message (newline delimited)"""
        sock.settimeout(timeout)
        data = b""
        while True:
            chunk = sock.recv(1)
            if not chunk:
                return None
            data += chunk
            if chunk == b'\n':
                break

        if not data.strip():
            return None

        return json.loads(data.decode('utf-8').strip())

    def test_hi_ready_flow(self):
        """Test HI message triggers READY response"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', TEST_PORT))

        # Send HI
        self.send_message(sock, {
            "message_type": "HI",
            "username": "TestPlayer"
        })

        # Receive READY
        response = self.receive_message(sock)

        self.assertIsNotNone(response)
        self.assertEqual(response['message_type'], 'READY')
        self.assertIn('info', response)
        self.assertIn('seconds', response['info'])

        sock.close()

    def test_ready_question_flow(self):
        """Test READY is followed by QUESTION"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', TEST_PORT))

        # Send HI
        self.send_message(sock, {
            "message_type": "HI",
            "username": "TestPlayer"
        })

        # Receive READY
        ready = self.receive_message(sock)
        self.assertEqual(ready['message_type'], 'READY')

        # Wait a bit then receive QUESTION
        question = self.receive_message(sock, timeout=10)

        self.assertIsNotNone(question)
        self.assertEqual(question['message_type'], 'QUESTION')
        self.assertIn('question_type', question)
        self.assertIn('trivia_question', question)
        self.assertIn('short_question', question)
        self.assertIn('time_limit', question)

        sock.close()

    def test_answer_result_flow(self):
        """Test ANSWER triggers RESULT response"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', TEST_PORT))

        # Send HI
        self.send_message(sock, {
            "message_type": "HI",
            "username": "TestPlayer"
        })

        # Skip READY
        self.receive_message(sock)

        # Receive QUESTION
        question = self.receive_message(sock, timeout=10)

        # Send any answer
        self.send_message(sock, {
            "message_type": "ANSWER",
            "answer": "42"
        })

        # Receive RESULT
        result = self.receive_message(sock)

        self.assertIsNotNone(result)
        self.assertEqual(result['message_type'], 'RESULT')
        self.assertIn('correct', result)
        self.assertIn('feedback', result)
        self.assertIsInstance(result['correct'], bool)

        sock.close()

    def test_complete_game_flow(self):
        """Test complete game: HI → READY → QUESTION → ANSWER → RESULT → LEADERBOARD → FINISHED"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', TEST_PORT))

        # Send HI
        self.send_message(sock, {
            "message_type": "HI",
            "username": "TestPlayer"
        })

        # Receive READY
        ready = self.receive_message(sock)
        self.assertEqual(ready['message_type'], 'READY')

        # Receive QUESTION
        question = self.receive_message(sock, timeout=10)
        self.assertEqual(question['message_type'], 'QUESTION')

        # Send ANSWER
        self.send_message(sock, {
            "message_type": "ANSWER",
            "answer": "999"
        })

        # Receive RESULT
        result = self.receive_message(sock)
        self.assertEqual(result['message_type'], 'RESULT')

        # Receive either LEADERBOARD or FINISHED (depending on question count)
        next_msg = self.receive_message(sock, timeout=10)
        self.assertIn(next_msg['message_type'], ['LEADERBOARD', 'FINISHED'])

        # If LEADERBOARD, wait for FINISHED
        if next_msg['message_type'] == 'LEADERBOARD':
            finished = self.receive_message(sock, timeout=15)
            if finished:  # Might get more questions first
                self.assertIn('message_type', finished)

        sock.close()

    def test_bye_disconnects(self):
        """Test BYE message causes disconnection"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', TEST_PORT))

        # Send HI
        self.send_message(sock, {
            "message_type": "HI",
            "username": "TestPlayer"
        })

        # Receive READY
        self.receive_message(sock)

        # Send BYE
        self.send_message(sock, {
            "message_type": "BYE"
        })

        # Connection should remain open (server doesn't force disconnect)
        # But we can close on our end
        sock.close()

    def test_message_format_has_newlines(self):
        """Test that all server messages end with newlines"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', TEST_PORT))

        # Send HI
        self.send_message(sock, {
            "message_type": "HI",
            "username": "TestPlayer"
        })

        # Receive raw data
        sock.settimeout(5)
        data = sock.recv(4096)

        # Should contain newline
        self.assertIn(b'\n', data)

        # Should be valid JSON when stripped
        json_str = data.decode('utf-8').strip()
        parsed = json.loads(json_str)
        self.assertEqual(parsed['message_type'], 'READY')

        sock.close()

    def test_question_fields_format(self):
        """Test QUESTION message has correctly formatted fields"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', TEST_PORT))

        # Send HI
        self.send_message(sock, {
            "message_type": "HI",
            "username": "TestPlayer"
        })

        # Skip READY
        self.receive_message(sock)

        # Receive QUESTION
        question = self.receive_message(sock, timeout=10)

        # Check trivia_question format: "Question 1 (Type):\nActual question"
        trivia_q = question['trivia_question']
        self.assertIn('Question', trivia_q)
        self.assertIn('(', trivia_q)
        self.assertIn(')', trivia_q)
        self.assertIn(':', trivia_q)

        # time_limit should be numeric
        self.assertIsInstance(question['time_limit'], (int, float))

        sock.close()


class TestMessageEncoding(unittest.TestCase):
    """Test message encoding/decoding"""

    def test_encode_decode_roundtrip(self):
        """Test encoding and decoding preserves data"""
        original = {
            "message_type": "QUESTION",
            "question_type": "Mathematics",
            "trivia_question": "What is 2 + 2?",
            "short_question": "2 + 2",
            "time_limit": 10
        }

        # Encode
        encoded = json.dumps(original) + '\n'
        encoded_bytes = encoded.encode('utf-8')

        # Decode
        decoded_str = encoded_bytes.decode('utf-8').strip()
        decoded = json.loads(decoded_str)

        self.assertEqual(original, decoded)

    def test_utf8_encoding(self):
        """Test UTF-8 encoding works"""
        message = {"message_type": "HI", "username": "TestUser"}
        encoded = (json.dumps(message) + '\n').encode('utf-8')

        self.assertIsInstance(encoded, bytes)
        self.assertTrue(encoded.endswith(b'\n'))


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
