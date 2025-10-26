# Trivia.NET Tests

This directory contains comprehensive tests for the Trivia.NET assignment.

## Test Structure

```
tests/
├── unit/                       # Unit tests (test individual components)
│   └── test_questions.py      # Question generation & solving tests
├── integration/               # Integration tests (test component interaction)
│   └── test_protocol.py       # Client-server protocol tests
├── system/                    # System tests (end-to-end scenarios)
│   └── test_complete_game.py  # Complete game flow tests
└── configs/                   # Test configuration files
    └── *.json                 # Various test configs
```

## Running Tests

### Run All Python Tests
```bash
python3 run_all_tests.py
```

### Run Specific Test Category
```bash
# Unit tests only
python3 -m unittest discover tests/unit -v

# Integration tests only
python3 -m unittest discover tests/integration -v

# System tests only
python3 -m unittest discover tests/system -v
```

### Run Single Test File
```bash
python3 tests/unit/test_questions.py
python3 tests/integration/test_protocol.py
python3 tests/system/test_complete_game.py
```

### Run Bash Tests (nc-based)
```bash
bash run_tests_nc.sh
```

## Test Categories Explained

### 1. Unit Tests (`tests/unit/`)
Test individual functions and components in isolation.

**What they test:**
- Question generation functions produce valid output
- Question solving functions return correct answers
- Helper functions work correctly
- No networking involved

**Example:**
- `test_questions.py`: Tests all question types (Math, Roman, IP, Network)

### 2. Integration Tests (`tests/integration/`)
Test how components work together, especially network protocol.

**What they test:**
- Message encoding/decoding
- Client-server message exchange
- Protocol flow (HI → READY → QUESTION → ANSWER → RESULT)
- Message format correctness
- Real socket connections

**Example:**
- `test_protocol.py`: Tests all message types and their flows

### 3. System Tests (`tests/system/`)
Test complete end-to-end scenarios as a user would experience them.

**What they test:**
- Complete game from start to finish
- Timing and delays
- Multiple questions in sequence
- Final standings
- Real server and client processes

**Example:**
- `test_complete_game.py`: Tests full game scenarios

## Writing New Tests

### Unit Test Template
```python
import unittest
from questions import *

class TestMyFeature(unittest.TestCase):
    def test_something(self):
        result = my_function()
        self.assertEqual(result, expected_value)

if __name__ == '__main__':
    unittest.main(verbosity=2)
```

### Integration Test Template
```python
import unittest
import socket
import json

class TestProtocolFeature(unittest.TestCase):
    def setUp(self):
        # Start server
        pass

    def tearDown(self):
        # Stop server
        pass

    def test_message_flow(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', PORT))
        # Test message exchange
        sock.close()
```

## Test Coverage Checklist

### ✅ Protocol Messages
- [x] HI message
- [x] READY message
- [x] QUESTION message
- [x] ANSWER message
- [x] RESULT message
- [ ] LEADERBOARD message (partial)
- [ ] FINISHED message (partial)
- [x] BYE message

### ✅ Question Types
- [x] Mathematics generation
- [x] Mathematics solving
- [x] Roman Numerals generation
- [x] Roman Numerals solving
- [x] Usable IP addresses generation
- [x] Usable IP addresses solving
- [x] Network/Broadcast generation
- [x] Network/Broadcast solving

### ✅ Game Flow
- [x] Single player complete game
- [x] Question timing
- [x] Answer validation
- [ ] Multi-player game
- [ ] Leaderboard tie-breaking
- [ ] Multiple winners scenario

### ✅ Client Modes
- [ ] Manual mode ("you")
- [x] Auto mode ("auto") - tested in system tests
- [ ] AI mode ("ai")

### ✅ Error Handling
- [ ] Missing config file
- [ ] Invalid config path
- [ ] Port binding failure
- [ ] Connection failure

## Adding More Tests

To achieve better coverage, consider adding:

1. **Multi-player tests**: Test with 2+ clients
2. **Leaderboard tests**: Test scoring, ties, rankings
3. **Error handling tests**: Test all error scenarios
4. **Client mode tests**: Test manual, auto, and AI modes thoroughly
5. **Edge case tests**: Disconnections, timeouts, empty answers
6. **Configuration tests**: Test different config values

## Tips for Testing

1. **Use descriptive test names**: `test_server_sends_ready_after_all_players_connect()`
2. **Test one thing per test**: Each test should verify one specific behavior
3. **Clean up resources**: Always close sockets and stop processes in tearDown()
4. **Use timeouts**: Socket operations should have timeouts to avoid hanging
5. **Test both success and failure**: Test what should work AND what should fail

## Common Issues

### Server doesn't stop
- Make sure `tearDown()` terminates the server process
- Use `kill()` if `terminate()` doesn't work
- Add sleep after cleanup: `time.sleep(0.3)`

### Port already in use
- Use different ports for different tests
- Make sure previous servers are killed
- Wait between tests: `time.sleep(0.5)`

### Tests hang
- Always use socket timeouts: `sock.settimeout(5)`
- Use subprocess timeouts: `process.wait(timeout=2)`
- Check for infinite loops in receive functions

### Race conditions
- Add delays after starting server: `time.sleep(0.5)`
- Use longer timeouts for complex operations
- Check message order assumptions

## Bash Test Alternative

The `run_tests_nc.sh` script provides bash-based tests using `nc` (netcat).

**Advantages:**
- Simple to write and understand
- Good for testing server in isolation
- Easy to debug with captured output

**Disadvantages:**
- Harder to test complex scenarios
- Timing is tricky
- Less control over client behavior

**When to use:**
- Quick server protocol tests
- Testing with raw socket data
- Verifying server output format

## For Full Marks

According to the assignment, for full marks you need:

1. ✅ **Functional tests**: Tests work and run automatically
2. ✅ **Use networking**: Tests use real socket connections
3. ✅ **Wide coverage**: Test both client and server behaviors
4. ✅ **At least one client**: Single client tests are sufficient

The tests provided cover these requirements. You can expand them for bonus learning or to ensure your implementation is robust.
