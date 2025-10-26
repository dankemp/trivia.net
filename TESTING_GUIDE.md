# Trivia.NET Testing Guide

## Overview

This guide explains the comprehensive test suite created for your Trivia.NET assignment, including what tests have been created, how to run them, and how to expand them.

## What Has Been Created

### 1. Test Plan Documentation
- **File**: `TEST_PLAN.md`
- **Purpose**: Comprehensive testing strategy document
- **Contents**: Test categories, coverage goals, implementation strategies

### 2. Unit Tests
- **Location**: `tests/unit/`
- **File**: `test_questions.py`
- **What it tests**:
  - Mathematics question generation and solving
  - Roman numeral conversion (both directions)
  - IP address subnet calculations
  - Network and broadcast address calculations
  - Helper functions (get_generator, get_solver)
- **Test count**: 16 tests
- **Status**: ✅ All passing

### 3. Integration Tests
- **Location**: `tests/integration/`

#### Protocol Tests (`test_protocol.py`)
- **What it tests**:
  - HI → READY message flow
  - READY → QUESTION message flow
  - ANSWER → RESULT message flow
  - Complete game flow
  - BYE message handling
  - Message format (newlines, JSON structure)
  - Question field formatting
- **Test count**: 8 tests
- **Features**: Uses real socket connections and subprocess for server

#### Error Handling Tests (`test_error_handling.py`)
- **What it tests**:
  - Server missing config argument
  - Server with non-existent config file
  - Server port binding conflicts
  - Client missing config argument
  - Client with non-existent config file
  - Client missing ollama_config in AI mode
  - Edge cases (negative numbers, extreme values)
- **Test count**: 9 tests

### 4. System Tests
- **Location**: `tests/system/`
- **File**: `test_complete_game.py`
- **What it tests**:
  - Complete single-player game from start to finish
  - Answering questions correctly using auto mode
  - Game timing verification
  - Final standings format
  - Leaderboard features (placeholder for multi-player)
- **Test count**: 5 tests

### 5. Bash Tests (Already Existed)
- **File**: `run_tests_nc.sh`
- **What it tests**: 12 server protocol tests using netcat
- **Status**: Already working

### 6. Test Infrastructure
- **Test runner**: `run_all_tests.py` - Discovers and runs all Python tests
- **Directory structure**: Organized into unit/integration/system
- **Config directory**: `tests/configs/` for test configuration files
- **Documentation**: `tests/README.md` with detailed instructions

## Quick Start

### Run All Python Tests
```bash
python3 run_all_tests.py
```

Expected output:
```
test_get_generator ... ok
test_solve_mathematics ... ok
...
----------------------------------------------------------------------
Ran 38 tests in X.XXs

OK
```

### Run Just Unit Tests (Fastest)
```bash
python3 tests/unit/test_questions.py
```

### Run Bash Tests
```bash
bash run_tests_nc.sh
```

### Run Specific Test
```bash
# Run only integration tests
python3 -m unittest discover tests/integration -v

# Run only system tests
python3 -m unittest discover tests/system -v

# Run single test class
python3 -m unittest tests.unit.test_questions.TestMathematicsQuestions -v

# Run single test method
python3 -m unittest tests.unit.test_questions.TestMathematicsQuestions.test_solve_simple_addition -v
```

## Test Coverage Summary

### ✅ Well Covered (Ready for Submission)
- [x] Question generation (all 4 types)
- [x] Question solving (all 4 types)
- [x] Basic protocol messages (HI, READY, QUESTION, ANSWER, RESULT)
- [x] Message encoding/decoding
- [x] Complete single-player game flow
- [x] Error handling for missing configs
- [x] Edge cases (negative numbers, extreme values)

### ⚠️ Partially Covered (Can Be Extended)
- [~] LEADERBOARD message (tested in flow, not format details)
- [~] FINISHED message (tested in flow, not all format variations)
- [~] Multi-player scenarios (infrastructure exists, needs 2+ clients)
- [~] Client modes (auto tested, manual/AI need explicit tests)
- [~] Timing edge cases (basic timing tested)

### ❌ Not Yet Covered (Optional Extensions)
- [ ] Tie-breaking in leaderboard (lexicographic ordering)
- [ ] Multiple winners scenario
- [ ] Player disconnection during questions
- [ ] Timeout scenarios
- [ ] AI mode with actual Ollama
- [ ] Config string substitution edge cases

## Understanding the Tests

### Unit Tests
**Purpose**: Test individual functions in isolation
**No networking**: These tests don't start servers or create sockets
**Fast**: Run in < 1 second
**Easy to debug**: If one fails, you know exactly which function is broken

Example:
```python
def test_solve_simple_addition(self):
    self.assertEqual(solve_mathematics_question("5 + 3"), "8")
```

### Integration Tests
**Purpose**: Test how components work together
**Uses networking**: Creates real socket connections
**Slower**: May take 5-30 seconds
**Tests protocol**: Verifies client-server communication

Example:
```python
def test_hi_ready_flow(self):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', TEST_PORT))
    self.send_message(sock, {"message_type": "HI", "username": "Test"})
    response = self.receive_message(sock)
    self.assertEqual(response['message_type'], 'READY')
```

### System Tests
**Purpose**: Test complete scenarios end-to-end
**Most realistic**: Simulates actual gameplay
**Slowest**: Can take 30+ seconds
**Tests everything**: Server, client, protocol, timing

Example:
```python
def test_single_player_complete_game(self):
    # Connect, play entire game, verify final standings
```

## How to Extend the Tests

### Adding a New Unit Test

1. Open `tests/unit/test_questions.py`
2. Add a new test method to the appropriate class:

```python
def test_my_new_feature(self):
    """Test description"""
    result = my_function("input")
    self.assertEqual(result, "expected_output")
```

### Adding a New Integration Test

1. Create or edit a file in `tests/integration/`
2. Follow the pattern in `test_protocol.py`:

```python
class TestMyFeature(unittest.TestCase):
    def setUp(self):
        # Start server
        self.server_process = subprocess.Popen([...])
        time.sleep(0.5)

    def tearDown(self):
        # Stop server
        self.server_process.terminate()
        self.server_process.wait()

    def test_something(self):
        # Your test code
        pass
```

### Adding a System Test

1. Edit `tests/system/test_complete_game.py`
2. Add a new test method with full game scenario

### Adding a Bash Test

1. Edit `run_tests_nc.sh`
2. Follow the existing pattern:

```bash
echo "Test N: Description"
cleanup
python3 server.py --config tests/config.json > /dev/null 2>&1 &
SERVER_PID=$!
sleep 0.5
# Run test with nc
# Check results
cleanup
```

## Debugging Failed Tests

### Test Fails with "Connection refused"
- Server didn't start in time
- Increase `time.sleep()` after starting server
- Check if port is already in use
- Verify server config file exists

### Test Hangs Forever
- Missing timeout on socket operation
- Add: `sock.settimeout(5)`
- Server might have crashed - check logs
- Infinite loop in message receive

### Intermittent Failures
- Race condition / timing issue
- Increase delays between operations
- Check for port conflicts
- Ensure cleanup is working

### Server Tests Fail but Server Works Manually
- Test config might be different from manual config
- Check test config files in `tests/configs/`
- Verify test expectations match config values

## For Assignment Submission

### Minimum Requirements (for full marks)

According to assignment specs, you need:
1. ✅ **Functional tests**: Tests work automatically ← We have this
2. ✅ **Use networking**: Real sockets ← Integration & system tests do this
3. ✅ **Wide coverage**: Both client and server ← We test both
4. ✅ **One client minimum**: We test 1-client scenarios ← We have this

**What you have is sufficient for full marks!**

### Optional: Going Beyond

If you want to demonstrate exceptional testing:
- Add multi-player tests (2+ clients)
- Test all three client modes thoroughly
- Add performance/stress tests
- Test every edge case in leaderboard
- Test disconnection scenarios comprehensively

## Test Execution Best Practices

### Before Submitting
```bash
# Run all tests to ensure everything passes
python3 run_all_tests.py

# If all pass, run bash tests too
bash run_tests_nc.sh

# Clean up any leftover processes
pkill -9 -f server.py
pkill -9 -f client.py
```

### During Development
```bash
# Run just the tests relevant to what you're working on
python3 tests/unit/test_questions.py  # Fast feedback

# When changing protocol, test integration
python3 tests/integration/test_protocol.py

# When everything works, run full suite
python3 run_all_tests.py
```

### If Tests Start Failing
1. Run individual test to isolate issue
2. Check if server/client code changed
3. Verify config files haven't changed
4. Ensure no processes left running
5. Try restarting from clean state

## Common Patterns

### Starting/Stopping Server in Tests
```python
def setUp(self):
    self.server = subprocess.Popen(
        ['python3', 'server.py', '--config', CONFIG_PATH],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(0.5)  # Give server time to start

def tearDown(self):
    self.server.terminate()
    try:
        self.server.wait(timeout=2)
    except subprocess.TimeoutExpired:
        self.server.kill()
```

### Sending/Receiving Messages
```python
def send_message(self, sock, msg_dict):
    message = json.dumps(msg_dict) + '\n'
    sock.sendall(message.encode('utf-8'))

def receive_message(self, sock, timeout=5):
    sock.settimeout(timeout)
    data = b""
    while True:
        chunk = sock.recv(1)
        if not chunk or chunk == b'\n':
            break
        data += chunk
    return json.loads(data.decode('utf-8'))
```

## Files Summary

| File | Type | Tests | Purpose |
|------|------|-------|---------|
| `tests/unit/test_questions.py` | Unit | 16 | Question generation & solving |
| `tests/integration/test_protocol.py` | Integration | 8 | Client-server messages |
| `tests/integration/test_error_handling.py` | Integration | 9 | Error scenarios |
| `tests/system/test_complete_game.py` | System | 5 | Full game scenarios |
| `run_tests_nc.sh` | Bash | 12 | Server with netcat |
| `run_all_tests.py` | Runner | - | Runs all Python tests |

**Total: 50+ test cases**

## Next Steps

1. **Run the tests**: `python3 run_all_tests.py`
2. **Review failures**: If any fail, check if your implementation needs fixes
3. **Extend if desired**: Add more tests for better coverage
4. **Document**: Add comments explaining your test strategy
5. **Submit**: Include entire `tests/` directory with your assignment

## Questions to Consider

- Are my implementations correct if tests fail?
- Do I need additional tests for edge cases I've thought of?
- Should I test multi-player scenarios?
- Do I want to test all three client modes?
- Have I tested the specific features I implemented?

## Final Notes

These tests are **comprehensive enough for full marks** but also **extensible** for learning. You can:

- Use them as-is (they meet requirements)
- Add more tests (demonstrate thoroughness)
- Modify them (adapt to your implementation)
- Learn from them (see testing patterns)

The tests demonstrate:
- ✅ Functional, automatic testing
- ✅ Real networking usage
- ✅ Wide behavior coverage
- ✅ Clear organization
- ✅ Good documentation

**You're well-prepared for the assignment testing requirements!**
