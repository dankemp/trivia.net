#!/bin/bash

# Client-Output Test Runner for Trivia.NET
# Tests the client's stdout output when playing against the server

PASSED=0
FAILED=0
TOTAL=0

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

pass_test() {
    echo -e "${GREEN}✓ PASS${NC}: $1"
    ((PASSED++))
    ((TOTAL++))
}

fail_test() {
    echo -e "${RED}✗ FAIL${NC}: $1"
    if [ -n "$2" ]; then
        echo "  Reason: $2"
    fi
    ((FAILED++))
    ((TOTAL++))
}

skip_test() {
    echo -e "${YELLOW}⊘ SKIP${NC}: $1"
    if [ -n "$2" ]; then
        echo "  Reason: $2"
    fi
}

cleanup() {
    # Kill any running servers and clients
    if [ -n "$SERVER_PID" ]; then
        kill -9 $SERVER_PID 2>/dev/null
        wait $SERVER_PID 2>/dev/null
    fi

    pkill -9 -f "python3 server.py" 2>/dev/null
    pkill -9 -f "python3 client.py" 2>/dev/null

    sleep 0.5
}

# Run a client test
# Args: test_name, server_config, client_config, input_file, check_function
run_client_test() {
    local test_name=$1
    local server_config=$2
    local client_config=$3
    local input_file=$4
    local check_function=$5
    local timeout_duration=${6:-15}

    local actual_output="tests/client_tests/actual/${test_name}.actual"

    # Start server
    python3 server.py --config "$server_config" > /dev/null 2>&1 &
    SERVER_PID=$!
    sleep 1

    # Check if server started
    if ! kill -0 $SERVER_PID 2>/dev/null; then
        fail_test "$test_name" "Server failed to start"
        return
    fi

    # Run client with timeout (use -u for unbuffered output)
    /usr/bin/timeout $timeout_duration python3 -u client.py --config "$client_config" < "$input_file" > "$actual_output" 2>&1
    local client_exit=$?

    # Check output using the provided check function
    $check_function "$actual_output" "$test_name"

    # Cleanup
    kill -9 $SERVER_PID 2>/dev/null
    wait $SERVER_PID 2>/dev/null
    SERVER_PID=""
    sleep 0.3
}

# Check functions for different test types

check_ready_message() {
    local output_file=$1
    local test_name=$2

    if grep -q "Game starts in" "$output_file"; then
        pass_test "$test_name"
    else
        fail_test "$test_name" "READY info not displayed"
        echo "  Output: $(head -5 "$output_file")"
    fi
}

check_question_displayed() {
    local output_file=$1
    local test_name=$2

    if grep -q "Question 1" "$output_file" && grep -q "What is" "$output_file"; then
        pass_test "$test_name"
    else
        fail_test "$test_name" "Question not properly displayed"
        echo "  Output: $(head -10 "$output_file")"
    fi
}

check_result_feedback() {
    local output_file=$1
    local test_name=$2

    if grep -q -E "(Correct|Wrong)" "$output_file"; then
        pass_test "$test_name"
    else
        fail_test "$test_name" "Result feedback not displayed"
        echo "  Output: $(cat "$output_file")"
    fi
}

check_final_standings() {
    local output_file=$1
    local test_name=$2

    if grep -q "FINAL STANDINGS" "$output_file" && grep -q "Winner:" "$output_file"; then
        pass_test "$test_name"
    else
        fail_test "$test_name" "Final standings not displayed"
        echo "  Output: $(tail -10 "$output_file")"
    fi
}

check_complete_game_flow() {
    local output_file=$1
    local test_name=$2

    local has_ready=$(grep -c "Game starts" "$output_file")
    local has_questions=$(grep -c "^Q [0-9]" "$output_file")
    local has_feedback=$(grep -c -E "(Correct|Wrong)" "$output_file")
    local has_final=$(grep -c "FINAL STANDINGS" "$output_file")

    if [ "$has_ready" -ge 1 ] && [ "$has_questions" -ge 2 ] && \
       [ "$has_feedback" -ge 2 ] && [ "$has_final" -ge 1 ]; then
        pass_test "$test_name"
    else
        fail_test "$test_name" "Missing game flow elements (Ready:$has_ready Q:$has_questions Feedback:$has_feedback Final:$has_final)"
        echo "  Output preview:"
        head -20 "$output_file" | sed 's/^/    /'
    fi
}

check_connection_failed() {
    local output_file=$1
    local test_name=$2

    if grep -q "Connection failed" "$output_file"; then
        pass_test "$test_name"
    else
        fail_test "$test_name" "Expected 'Connection failed' message"
    fi
}

# =============================================================================
# TEST SUITE
# =============================================================================

echo "=========================================="
echo "  Trivia.NET Client-Output Test Suite"
echo "=========================================="
echo ""

cleanup

# Create actual output directory
mkdir -p tests/client_tests/actual

# -----------------------------------------------------------------------------
# TEST 1: Client Displays READY Message
# -----------------------------------------------------------------------------
echo "TEST 1: Client displays READY message after connecting"
run_client_test \
    "test_01" \
    "tests/client_tests/configs/server_1player_1question.json" \
    "tests/client_tests/configs/client_manual.json" \
    "tests/client_tests/inputs/test_01_connect_disconnect.in" \
    "check_ready_message" \
    10

# -----------------------------------------------------------------------------
# TEST 2: Client Displays QUESTION Message
# -----------------------------------------------------------------------------
echo "TEST 2: Client displays question received from server"
run_client_test \
    "test_02" \
    "tests/client_tests/configs/server_1player_1question.json" \
    "tests/client_tests/configs/client_manual.json" \
    "tests/client_tests/inputs/test_01_connect_disconnect.in" \
    "check_question_displayed" \
    10

# -----------------------------------------------------------------------------
# TEST 3: Client Displays RESULT Feedback
# -----------------------------------------------------------------------------
echo "TEST 3: Client displays result feedback after answering"
run_client_test \
    "test_03" \
    "tests/client_tests/configs/server_1player_1question.json" \
    "tests/client_tests/configs/client_manual.json" \
    "tests/client_tests/inputs/test_02_answer_question.in" \
    "check_result_feedback" \
    12

# -----------------------------------------------------------------------------
# TEST 4: Complete Game Flow (Manual Mode)
# -----------------------------------------------------------------------------
echo "TEST 4: Complete game flow with 2 questions (manual mode)"
run_client_test \
    "test_04" \
    "tests/client_tests/configs/server_1player_2questions.json" \
    "tests/client_tests/configs/client_manual.json" \
    "tests/client_tests/inputs/test_03_complete_game.in" \
    "check_complete_game_flow" \
    20

# -----------------------------------------------------------------------------
# TEST 5: Auto Mode Completes Game
# -----------------------------------------------------------------------------
echo "TEST 5: Auto mode client can complete a game"

# For auto mode, we just need CONNECT and EXIT since it answers automatically
cat > tests/client_tests/inputs/test_05_auto.in << 'EOF'
CONNECT localhost:8002
EXIT
EOF

run_client_test \
    "test_05" \
    "tests/client_tests/configs/server_1player_2questions.json" \
    "tests/client_tests/configs/client_auto.json" \
    "tests/client_tests/inputs/test_05_auto.in" \
    "check_complete_game_flow" \
    20

# -----------------------------------------------------------------------------
# TEST 6: Connection Failure Handling
# -----------------------------------------------------------------------------
echo "TEST 6: Client handles connection failure gracefully"

# Try to connect to non-existent server
cat > tests/client_tests/inputs/test_06_connect_fail.in << 'EOF'
CONNECT localhost:9999
EXIT
EOF

# Don't start a server for this test
SERVER_PID=""
/usr/bin/timeout 3 python3 -u client.py --config "tests/client_tests/configs/client_manual.json" \
    < "tests/client_tests/inputs/test_06_connect_fail.in" \
    > "tests/client_tests/actual/test_06.actual" 2>&1

check_connection_failed "tests/client_tests/actual/test_06.actual" "test_06"

# -----------------------------------------------------------------------------
# SUMMARY
# -----------------------------------------------------------------------------
echo ""
echo "=========================================="
echo "           TEST SUMMARY"
echo "=========================================="
echo "Total Tests:  $TOTAL"
echo -e "Passed:       ${GREEN}$PASSED${NC}"
echo -e "Failed:       ${RED}$FAILED${NC}"
echo "=========================================="

cleanup

if [ $FAILED -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ All tests passed!${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}✗ Some tests failed${NC}"
    echo ""
    echo "To debug failed tests, check the actual output files in:"
    echo "  tests/client_tests/actual/"
    exit 1
fi
