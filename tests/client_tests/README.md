# Client-Output Testing Suite for Trivia.NET

This testing suite uses the **recommended Method 1** from the assignment: testing your client's output when it plays against your server.

## Why This Approach?

✅ **Recommended by assignment** - Tests what your client prints to stdout
✅ **More reliable** - No complex netcat timing issues
✅ **Easier to debug** - Just compare client output
✅ **Tests your actual code** - Uses your real client implementation
✅ **Familiar pattern** - Similar to Assignment 1 testing style

## Directory Structure

```
tests/client_tests/
├── README.md                 # This file
├── run_client_tests.sh       # Main test runner
├── configs/                  # Server and client configurations
│   ├── server_1player_1question.json
│   ├── server_1player_2questions.json
│   ├── client_manual.json
│   └── client_auto.json
├── inputs/                   # Test input files (.in)
│   ├── test_01_connect_disconnect.in
│   ├── test_02_answer_question.in
│   └── test_03_complete_game.in
└── actual/                   # Actual output (generated during tests)
    ├── test_01.actual
    ├── test_02.actual
    └── ...
```

## Running Tests

### Run All Tests
```bash
bash tests/client_tests/run_client_tests.sh
```

### Expected Output
```
==========================================
  Trivia.NET Client-Output Test Suite
==========================================

TEST 1: Client displays READY message after connecting
✓ PASS: test_01

TEST 2: Client displays question received from server
✓ PASS: test_02

TEST 3: Client displays result feedback after answering
✓ PASS: test_03

TEST 4: Complete game flow with 2 questions (manual mode)
✓ PASS: test_04

TEST 5: Auto mode client can complete a game
✓ PASS: test_05

TEST 6: Client handles connection failure gracefully
✓ PASS: test_06

==========================================
           TEST SUMMARY
==========================================
Total Tests:  6
Passed:       6
Failed:       0
==========================================

✓ All tests passed!
```

## Test Cases Explained

### TEST 1: READY Message Display
**What it tests:** Client prints the READY message info when game starts
**Input:** Connect and disconnect
**Checks for:** "Game starts in" message

### TEST 2: Question Display
**What it tests:** Client displays questions from server
**Input:** Connect and wait for question
**Checks for:** "Question 1" and "What is" in output

### TEST 3: Result Feedback
**What it tests:** Client displays feedback after answering
**Input:** Connect, answer a question, disconnect
**Checks for:** "Correct" or "Wrong" in output

### TEST 4: Complete Game Flow (Manual Mode)
**What it tests:** Full game with manual answer input
**Input:** Connect, answer 2 questions, disconnect
**Checks for:** READY, questions, feedback, and final standings

### TEST 5: Auto Mode
**What it tests:** Auto mode can play and complete a game
**Input:** Just connect (auto mode answers automatically)
**Checks for:** Complete game flow including final standings

### TEST 6: Connection Failure
**What it tests:** Client handles failed connections gracefully
**Input:** Try to connect to non-existent server
**Checks for:** "Connection failed" message

## How Tests Work

1. **Start Server**: Test runner starts server with specific config
2. **Run Client**: Client reads input from `.in` file
3. **Capture Output**: Client's stdout is saved to `.actual` file
4. **Check Patterns**: Test checks for expected patterns/keywords
5. **Report Result**: Pass or fail with helpful error messages
6. **Cleanup**: Kill server and client processes

## Debugging Failed Tests

If a test fails, check the actual output:

```bash
# View actual output of test 1
cat tests/client_tests/actual/test_01.actual

# Compare with what the test expected
# (Check the test's check_function in run_client_tests.sh)
```

## Adding New Tests

To add a new test:

1. **Create server config** (if needed):
   ```bash
   tests/client_tests/configs/server_mytest.json
   ```

2. **Create client config** (if needed):
   ```bash
   tests/client_tests/configs/client_mytest.json
   ```

3. **Create input file**:
   ```bash
   tests/client_tests/inputs/test_07_mytest.in
   ```
   Content example:
   ```
   CONNECT localhost:8003
   my_answer
   DISCONNECT
   EXIT
   ```

4. **Add test to run_client_tests.sh**:
   ```bash
   echo "TEST 7: My new test"
   run_client_test \
       "test_07" \
       "tests/client_tests/configs/server_mytest.json" \
       "tests/client_tests/configs/client_mytest.json" \
       "tests/client_tests/inputs/test_07_mytest.in" \
       "check_my_custom_function" \
       15
   ```

5. **Create check function** (if needed):
   ```bash
   check_my_custom_function() {
       local output_file=$1
       local test_name=$2

       if grep -q "expected_pattern" "$output_file"; then
           pass_test "$test_name"
       else
           fail_test "$test_name" "Pattern not found"
       fi
   }
   ```

## Tips for Writing Tests

### Good Test Practices
- ✅ Check for patterns, not exact text (questions are random)
- ✅ Use generous timeouts for slow machines
- ✅ Test one behavior per test
- ✅ Give descriptive test names
- ✅ Check for key protocol messages

### What to Check For
Since questions are randomly generated, check for:
- Message patterns: "Question 1", "Q 2", etc.
- Format strings: "What is", "Calculate", etc.
- Feedback keywords: "Correct", "Wrong", "Winner"
- Protocol flow: READY → QUESTION → RESULT → FINISHED

### What NOT to Check
- ❌ Exact question content (random)
- ❌ Specific numbers in questions
- ❌ Exact point values (depends on answers)

## Advantages Over nc Tests

| Feature | Client-Output Tests | nc Tests |
|---------|-------------------|----------|
| Reliability | ✅ High | ⚠️ Low (timing issues) |
| Debugging | ✅ Easy | ⚠️ Hard |
| Maintenance | ✅ Simple | ⚠️ Complex |
| Real-world | ✅ Tests actual client | ⚠️ Tests server only |
| Speed | ✅ Fast | ⚠️ Slow (many sleeps) |

## Common Issues

### Test hangs
- Increase timeout in `run_client_test` call
- Check if server/client has infinite loop
- Ensure DISCONNECT and EXIT are in input file

### "Connection refused"
- Server might not have started in time
- Port might be in use
- Increase sleep after server start

### Wrong output
- Check actual output file to see what client printed
- Verify server config matches what test expects
- Ensure client is reading input correctly

## For Assignment Submission

These tests satisfy the assignment requirements:
- ✅ Functional tests that run automatically
- ✅ Properly use networking (real sockets)
- ✅ Wide coverage of behaviors
- ✅ Test both client and server
- ✅ At least one client (we test with one)

You can extend these tests or use them as-is for full marks on the testing component.
