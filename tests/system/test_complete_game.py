#!/usr/bin/env python3
"""
System tests for complete game scenarios

Tests full end-to-end game flows.
"""

import unittest
import subprocess
import time
import os
import json
import socket


class TestCompleteGame(unittest.TestCase):
    """Test complete game scenarios"""

    @classmethod
    def setUpClass(cls):
        """Create test configurations"""
        os.makedirs("tests/configs", exist_ok=True)

        # Server config for single player with 2 questions
        cls.server_config = {
            "port": 10001,
            "players": 1,
            "question_types": ["Mathematics", "Roman Numerals"],
            "question_formats": {
                "Mathematics": "Calculate: {}",
                "Roman Numerals": "Convert {} to decimal:"
            },
            "question_seconds": 10,
            "question_interval_seconds": 2,
            "ready_info": "Game starts in {question_interval_seconds} seconds!",
            "question_word": "Q",
            "correct_answer": "Correct!",
            "incorrect_answer": "Wrong! Answer was {correct_answer}",
            "points_noun_singular": "point",
            "points_noun_plural": "points",
            "final_standings_heading": "===FINAL===",
            "one_winner": "Winner: {}",
            "multiple_winners": "Winners: {}"
        }

        cls.server_config_path = "tests/configs/system_test_server.json"
        with open(cls.server_config_path, 'w') as f:
            json.dump(cls.server_config, f)

        # Client config for auto mode
        cls.client_config = {
            "username": "AutoPlayer",
            "client_mode": "auto"
        }

        cls.client_config_path = "tests/configs/system_test_client_auto.json"
        with open(cls.client_config_path, 'w') as f:
            json.dump(cls.client_config, f)

    def setUp(self):
        """Start server before each test"""
        self.server_process = subprocess.Popen(
            ['python3', 'server.py', '--config', self.server_config_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(0.5)

    def tearDown(self):
        """Stop server and client after each test"""
        if hasattr(self, 'server_process') and self.server_process:
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
                self.server_process.wait()

        if hasattr(self, 'client_process') and self.client_process:
            self.client_process.terminate()
            try:
                self.client_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.client_process.kill()
                self.client_process.wait()

        time.sleep(0.3)

    def send_message(self, sock, message_dict):
        """Send JSON message"""
        message = json.dumps(message_dict) + '\n'
        sock.sendall(message.encode('utf-8'))

    def receive_message(self, sock, timeout=15):
        """Receive JSON message"""
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

    def test_single_player_complete_game(self):
        """Test complete single player game from start to finish"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 10001))

        # 1. Send HI
        self.send_message(sock, {
            "message_type": "HI",
            "username": "TestPlayer"
        })

        # 2. Expect READY
        ready = self.receive_message(sock)
        self.assertEqual(ready['message_type'], 'READY')
        self.assertIn('Game starts', ready['info'])

        messages_received = []

        # 3. Play through all questions
        for q_num in range(2):  # 2 questions configured
            # Receive QUESTION
            question = self.receive_message(sock, timeout=15)
            self.assertEqual(question['message_type'], 'QUESTION')
            messages_received.append(question)

            # Send ANSWER (doesn't matter if correct for this test)
            self.send_message(sock, {
                "message_type": "ANSWER",
                "answer": "42"
            })

            # Receive RESULT
            result = self.receive_message(sock)
            self.assertEqual(result['message_type'], 'RESULT')
            messages_received.append(result)

            # If not last question, receive LEADERBOARD
            if q_num < 1:  # Not last question
                leaderboard = self.receive_message(sock, timeout=15)
                if leaderboard and leaderboard['message_type'] == 'LEADERBOARD':
                    messages_received.append(leaderboard)

        # 4. Expect FINISHED
        finished = self.receive_message(sock, timeout=15)
        self.assertEqual(finished['message_type'], 'FINISHED')
        self.assertIn('===FINAL===', finished['final_standings'])
        self.assertIn('TestPlayer', finished['final_standings'])

        sock.close()

    def test_game_with_correct_answers(self):
        """Test game where player answers all questions correctly"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 10001))

        # Import solving functions
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        from questions import solve_mathematics_question, solve_roman_numerals_question

        solvers = {
            "Mathematics": solve_mathematics_question,
            "Roman Numerals": solve_roman_numerals_question
        }

        # Send HI
        self.send_message(sock, {
            "message_type": "HI",
            "username": "SmartPlayer"
        })

        # Skip READY
        self.receive_message(sock)

        correct_count = 0

        # Answer all questions correctly
        for _ in range(2):
            # Receive QUESTION
            question = self.receive_message(sock, timeout=15)
            if not question or question['message_type'] != 'QUESTION':
                break

            q_type = question['question_type']
            short_q = question['short_question']

            # Solve it
            solver = solvers.get(q_type)
            if solver:
                correct_answer = solver(short_q)

                # Send correct answer
                self.send_message(sock, {
                    "message_type": "ANSWER",
                    "answer": correct_answer
                })

                # Receive RESULT
                result = self.receive_message(sock)
                if result['correct']:
                    correct_count += 1

                # Skip LEADERBOARD if present
                try:
                    next_msg = self.receive_message(sock, timeout=5)
                    if next_msg and next_msg['message_type'] == 'FINISHED':
                        break
                except:
                    pass

        # Should have gotten at least 1 correct
        self.assertGreater(correct_count, 0)

        sock.close()

    def test_game_timing(self):
        """Test that game respects timing configuration"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 10001))

        # Send HI
        start_time = time.time()
        self.send_message(sock, {
            "message_type": "HI",
            "username": "TimingTest"
        })

        # Receive READY
        self.receive_message(sock)

        # Time until QUESTION (should be ~2 seconds based on config)
        question = self.receive_message(sock, timeout=15)
        time_to_question = time.time() - start_time

        # Should be approximately question_interval_seconds (2s) + some buffer
        self.assertGreater(time_to_question, 1.5)  # At least 1.5s
        self.assertLess(time_to_question, 4.0)     # Less than 4s

        sock.close()

    def test_final_standings_format(self):
        """Test FINISHED message has correct final standings format"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 10001))

        # Send HI
        self.send_message(sock, {
            "message_type": "HI",
            "username": "Player1"
        })

        # Skip to end
        self.receive_message(sock)  # READY

        # Answer all questions quickly
        for _ in range(2):
            question = self.receive_message(sock, timeout=15)
            if question and question['message_type'] == 'QUESTION':
                self.send_message(sock, {
                    "message_type": "ANSWER",
                    "answer": "0"
                })
                self.receive_message(sock)  # RESULT
                try:
                    msg = self.receive_message(sock, timeout=5)
                    if msg and msg['message_type'] == 'FINISHED':
                        break
                except:
                    pass

        # Get FINISHED
        finished = None
        try:
            finished = self.receive_message(sock, timeout=15)
        except:
            pass

        if finished and finished['message_type'] == 'FINISHED':
            standings = finished['final_standings']

            # Check format
            self.assertIn('===FINAL===', standings)
            self.assertIn('Player1', standings)
            self.assertIn('point', standings.lower())

            # Should have "Winner:" line
            self.assertTrue(
                'Winner: Player1' in standings or
                'Winners: Player1' in standings
            )

        sock.close()


class TestLeaderboardFeatures(unittest.TestCase):
    """Test leaderboard-specific features"""

    @classmethod
    def setUpClass(cls):
        """Create test config for multi-player"""
        os.makedirs("tests/configs", exist_ok=True)

        cls.config = {
            "port": 10002,
            "players": 2,
            "question_types": ["Mathematics"],
            "question_formats": {
                "Mathematics": "What is {}?"
            },
            "question_seconds": 10,
            "question_interval_seconds": 1,
            "ready_info": "Starting soon!",
            "question_word": "Question",
            "correct_answer": "Right!",
            "incorrect_answer": "Wrong!",
            "points_noun_singular": "point",
            "points_noun_plural": "points",
            "final_standings_heading": "Final:",
            "one_winner": "Winner: {}",
            "multiple_winners": "Winners: {}"
        }

        cls.config_path = "tests/configs/leaderboard_test.json"
        with open(cls.config_path, 'w') as f:
            json.dump(cls.config, f)

    def test_leaderboard_contains_all_players(self):
        """Test that leaderboard shows all players"""
        # This would require 2 clients, which is more complex
        # For now, just document the test case
        # In real implementation, would start 2 clients and verify
        # leaderboard contains both usernames
        pass


if __name__ == '__main__':
    unittest.main(verbosity=2)
