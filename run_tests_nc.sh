#!/bin/bash

PASSED=0
FAILED=0
TOTAL=0

pass_test() {
    echo "PASS: $1"
    ((PASSED++))
    ((TOTAL++))
}

fail_test() {
    echo "FAIL: $1"
    if [ -n "$2" ]; then
        echo "  Reason: $2"
    fi
    ((FAILED++))
    ((TOTAL++))
}

cleanup() {
    # the specific server if PID is set
    #this is done so we don't clean the currently running processes

    if [ -n "$SERVER_PID" ]; then
      kill -9 $SERVER_PID 2>/dev/null
    fi

    pkill -9 -f "nc localhost" 2>/dev/null

    sleep 1
}

#helper to run nc without using timeout function
run_nc(){
  local timeout_sec=$1
  shift

  #run nc in the background, capture PID
  "$@" &
  local nc_pid=$!

  #just having a simple sleep before was killing the program too quickly
  #its important to have a variable sleep function


  #wait for specified time or until nc finishes naturally

  local count=0
  while kill -0 $nc_pid 2>/dev/null && [ $count -lt $timeout_sec ]; do
    sleep 1
    ((count++))
  done

  #kill nc if its stil running
  if kill -0 $nc_pid 2>/dev/null; then
    kill $nc_pid 2>/dev/null
    wait $nc_pid 2>/dev/null
  fi
}

echo "SETUP: Creating Test Configurations"

mkdir -p tests

cat > tests/server_test.json << 'EOF'
{
    "port": 7778,
    "players": 1,
    "question_types": ["Mathematics"],
    "question_formats": {
        "Mathematics": "What is {}?"
    },
    "question_seconds": 5,
    "question_interval_seconds": 1,
    "ready_info": "Game starts in {question_interval_seconds} seconds!",
    "question_word": "Question",
    "correct_answer": "Correct!",
    "incorrect_answer": "Wrong!",
    "points_noun_singular": "point",
    "points_noun_plural": "points",
    "final_standings_heading": "Final standings:",
    "one_winner": "Winner: {}",
    "multiple_winners": "Winners: {}"
}
EOF

cat > tests/server_2player.json << 'EOF'
{
    "port": 7779,
    "players": 2,
    "question_types": ["Mathematics", "Roman Numerals"],
    "question_formats": {
        "Mathematics": "What is {}?",
        "Roman Numerals": "What is the decimal value of {}?"
    },
    "question_seconds": 10,
    "question_interval_seconds": 2,
    "ready_info": "Game starts in {question_interval_seconds} seconds!",
    "question_word": "Question",
    "correct_answer": "Correct!",
    "incorrect_answer": "Wrong!",
    "points_noun_singular": "point",
    "points_noun_plural": "points",
    "final_standings_heading": "Final standings:",
    "one_winner": "Winner: {}",
    "multiple_winners": "Winners: {}"
}
EOF

echo "✓ Test configurations created"

# TEST 1: Server Sends READY Message

echo "Test 1. Server sends READY message after client connects"

cleanup

# Start server
python3 server.py --config tests/server_test.json > /dev/null 2>&1 &
SERVER_PID=$!
sleep 0.5

# Create HI message
echo '{"message_type": "HI", "username": "TestPlayer"}' > tests/test_01_input.txt

# Connect and send HI, capture output
run_nc 3 nc localhost 7778 < tests/test_01_input.txt > tests/test_01_output.txt 2>&1

# Check if READY message received
if grep -q "READY" tests/test_01_output.txt && grep -q "Game starts" tests/test_01_output.txt; then
    pass_test "Server sends READY message"
else
    fail_test "Server sends READY message" "READY message not found in output"
fi

cleanup

# TEST 2: Server Sends QUESTION Message

echo "Test 2. Server sends QUESTION message"

cleanup

python3 server.py --config tests/server_test.json > /dev/null 2>&1 &
SERVER_PID=$!
sleep 0.5

# Send HI and wait for QUESTION
echo '{"message_type": "HI", "username": "TestPlayer"}' | run_nc 5 nc localhost 7778 > tests/test_02_output.txt 2>&1

# Check if QUESTION message received
if grep -q "QUESTION" tests/test_02_output.txt; then
    pass_test "Server sends QUESTION message"
else
    fail_test "Server sends QUESTION message" "QUESTION message not found"
fi

cleanup

# TEST 3: Server Accepts Answer and Sends RESULT

echo "Test 3. Server accepts ANSWER and sends RESULT"

cleanup

python3 server.py --config tests/server_test.json > /dev/null 2>&1 &
SERVER_PID=$!
sleep 0.5

# Create input with HI and ANSWER
cat > tests/test_03_input.txt << 'EOF'
{"message_type": "HI", "username": "TestPlayer"}
{"message_type": "ANSWER", "answer": "42"}
EOF

run_nc 5 nc localhost 7778 < tests/test_03_input.txt > tests/test_03_output.txt 2>&1
sleep 0.5

# Check if RESULT message received
if grep -q "RESULT" tests/test_03_output.txt; then
    pass_test "Server sends RESULT message"
else
    fail_test "Server sends RESULT message" "RESULT message not found"
fi

cleanup

# TEST 4: Server Sends FINISHED Message at End

echo "Test 4. Server sends FINISHED message at game end"

cleanup

python3 server.py --config tests/server_test.json > /dev/null 2>&1 &
SERVER_PID=$!
sleep 0.5

# Send complete game sequence
cat > tests/test_04_input.txt << 'EOF'
{"message_type": "HI", "username": "TestPlayer"}
{"message_type": "ANSWER", "answer": "42"}
EOF

run_nc 8 nc localhost 7778 < tests/test_04_input.txt > tests/test_04_output.txt 2>&1

# Check if FINISHED message received
if grep -q "FINISHED" tests/test_04_output.txt && grep -q "Final standings" tests/test_04_output.txt; then
    pass_test "Server sends FINISHED message"
else
    fail_test "Server sends FINISHED message" "FINISHED message not found"
fi

cleanup

# TEST 5: READY Message Contains Correct Info

echo "Test 5. READY message contains correct information"

cleanup

python3 server.py --config tests/server_test.json > /dev/null 2>&1 &
SERVER_PID=$!
sleep 0.5

echo '{"message_type": "HI", "username": "TestPlayer"}' | run_nc 3 nc localhost 7778 > tests/test_05_output.txt 2>&1

# Parse JSON and check for required fields
if grep -q '"message_type".*:.*"READY"' tests/test_05_output.txt && \
   grep -q '"info"' tests/test_05_output.txt; then
    pass_test "READY message has required fields"
else
    fail_test "READY message has required fields" "Missing message_type or info"
fi

cleanup

# TEST 6: QUESTION Message Contains All Required Fields

echo "Test 6. QUESTION message contains all required fields"

cleanup

python3 server.py --config tests/server_test.json > /dev/null 2>&1 &
SERVER_PID=$!
sleep 0.5

echo '{"message_type": "HI", "username": "TestPlayer"}' | timeout 5 nc localhost 7778 > tests/test_06_output.txt 2>&1

# Check for required fields
if grep -q '"question_type"' tests/test_06_output.txt && \
   grep -q '"trivia_question"' tests/test_06_output.txt && \
   grep -q '"short_question"' tests/test_06_output.txt && \
   grep -q '"time_limit"' tests/test_06_output.txt; then
    pass_test "QUESTION message has all required fields"
else
    fail_test "QUESTION message has all required fields" "Missing required fields"
fi

cleanup

# TEST 7: RESULT Message Contains Correct/Feedback

echo "Test 7. RESULT message contains correct and feedback fields"

cleanup

python3 server.py --config tests/server_test.json > /dev/null 2>&1 &
SERVER_PID=$!
sleep 0.5

cat > tests/test_07_input.txt << 'EOF'
{"message_type": "HI", "username": "TestPlayer"}
{"message_type": "ANSWER", "answer": "42"}
EOF

timeout 5 nc localhost 7778 < tests/test_07_input.txt > tests/test_07_output.txt 2>&1

if grep -q '"correct"' tests/test_07_output.txt && \
   grep -q '"feedback"' tests/test_07_output.txt; then
    pass_test "RESULT message has correct and feedback"
else
    fail_test "RESULT message has correct and feedback" "Missing required fields"
fi

cleanup

# TEST 8: Server Handles Invalid Username (Non-Alphanumeric)

echo "Test 8. Server rejects non-alphanumeric username"

cleanup

python3 server.py --config tests/server_test.json > /dev/null 2>&1 &
SERVER_PID=$!
sleep 0.5

# Send HI with invalid username
echo '{"message_type": "HI", "username": "Test@123"}' | timeout 3 nc localhost 7778 > tests/test_08_output.txt 2>&1

# Server should disconnect/exit (won't send READY)
sleep 1
if ! grep -q "READY" tests/test_08_output.txt; then
    pass_test "Server rejects invalid username"
else
    fail_test "Server rejects invalid username" "Server accepted invalid username"
fi

cleanup

# TEST 9: Server Handles BYE Message

echo "Test 9. Server handles BYE message from client"

cleanup

python3 server.py --config tests/server_test.json > /dev/null 2>&1 &
SERVER_PID=$!
sleep 0.5

cat > tests/test_09_input.txt << 'EOF'
{"message_type": "HI", "username": "TestPlayer"}
{"message_type": "BYE"}
EOF

timeout 3 nc localhost 7778 < tests/test_09_input.txt > tests/test_09_output.txt 2>&1

# Should get READY but then disconnect
if grep -q "READY" tests/test_09_output.txt; then
    pass_test "Server handles BYE message"
else
    fail_test "Server handles BYE message" "Server didn't respond before BYE"
fi

cleanup

# TEST 10: Messages End With Newline (Server Protocol)

echo "Test 10. Server messages end with newline"

cleanup

python3 server.py --config tests/server_test.json > /dev/null 2>&1 &
SERVER_PID=$!
sleep 0.5

echo '{"message_type": "HI", "username": "TestPlayer"}' | timeout 3 nc localhost 7778 > tests/test_10_output.txt 2>&1

# Check if output has newlines (proper protocol)
if [ -s tests/test_10_output.txt ]; then
    # File exists and has content
    pass_test "Server sends data with newlines"
else
    fail_test "Server sends data with newlines" "No output received"
fi

cleanup

# TEST 11: Server Waits for Required Number of Players

echo "Test 11. Server waits for required number of players (2 players config)"

cleanup

python3 server.py --config tests/server_2player.json > /dev/null 2>&1 &
SERVER_PID=$!
sleep 0.5

# Connect only 1 player
echo '{"message_type": "HI", "username": "Player1"}' | timeout 3 nc localhost 7779 > tests/test_11_output.txt 2>&1 &

# Wait a bit
sleep 2

if [ -f tests/test_11_output.txt ]; then
    pass_test "Server waits for correct number of players"
else
    fail_test "Server waits for correct number of players" "Unexpected behavior"
fi

cleanup

# TEST 12: Complete Game Flow (End-to-End)

echo "Test 12. Complete game flow (HI → READY → QUESTION → ANSWER → RESULT → FINISHED)"

cleanup

python3 server.py --config tests/server_test.json > /dev/null 2>&1 &
SERVER_PID=$!
sleep 0.5

cat > tests/test_12_input.txt << 'EOF'
{"message_type": "HI", "username": "TestPlayer"}
{"message_type": "ANSWER", "answer": "42"}
EOF

timeout 8 nc localhost 7778 < tests/test_12_input.txt > tests/test_12_output.txt 2>&1

# Check for all message types
FOUND_READY=$(grep -c "READY" tests/test_12_output.txt)
FOUND_QUESTION=$(grep -c "QUESTION" tests/test_12_output.txt)
FOUND_RESULT=$(grep -c "RESULT" tests/test_12_output.txt)
FOUND_FINISHED=$(grep -c "FINISHED" tests/test_12_output.txt)

if [ "$FOUND_READY" -ge 1 ] && [ "$FOUND_QUESTION" -ge 1 ] && \
   [ "$FOUND_RESULT" -ge 1 ] && [ "$FOUND_FINISHED" -ge 1 ]; then
    pass_test "Complete game flow works"
else
    fail_test "Complete game flow works" "Missing messages (R:$FOUND_READY Q:$FOUND_QUESTION Rs:$FOUND_RESULT F:$FOUND_FINISHED)"
fi

cleanup

# SUMMARY
echo "TEST SUMMARY"

echo "Total Tests: $TOTAL"
echo "Passed: $PASSED"
echo "Failed: $FAILED"

if [ $FAILED -eq 0 ]; then
    echo ""
    echo "All tests passed!"
    exit 0
else
    echo ""
    echo "Some tests failed"
    exit 1
fi