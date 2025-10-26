# Trivia.NET Test Plan

## Overview
This document outlines the comprehensive testing strategy for the Trivia.NET assignment.

## Test Categories

### 1. Unit Tests (Python)
Test individual components in isolation.

#### Question Module Tests
- **Test Mathematics Question Generation**
  - Verify 2-5 operands
  - Verify operands in range [1, 100]
  - Verify only + and - operators

- **Test Mathematics Question Solving**
  - Test simple addition: "5 + 3" → "8"
  - Test simple subtraction: "10 - 4" → "6"
  - Test mixed operations: "5 + 3 - 2" → "6"
  - Test negative results: "5 - 10" → "-5"
  - Test complex: "100 - 50 + 25 - 10 + 5" → "70"

- **Test Roman Numerals Generation**
  - Verify range [1, 3999]
  - Verify valid Roman numeral format

- **Test Roman Numerals Solving**
  - Test simple: "XIV" → "14"
  - Test subtractive: "IX" → "9"
  - Test large: "MCMXCIV" → "1994"
  - Test edge cases: "I" → "1", "MMMCMXCIX" → "3999"

- **Test IP Address Questions**
  - Verify valid CIDR notation
  - Test usable addresses: "192.168.1.0/24" → "254"
  - Test network/broadcast: "192.168.1.37/24" → "192.168.1.0 and 192.168.1.255"
  - Test edge cases: /30, /31 subnets

### 2. Integration Tests (Server + Client)
Test server and client interaction.

#### Message Protocol Tests
- **Test HI Message**
  - Client sends HI with username
  - Server accepts valid username
  - Server stores player info

- **Test READY Message**
  - Server waits for correct number of players
  - Server sends READY to all players
  - READY contains correct info field

- **Test QUESTION Message**
  - Server sends QUESTION after ready_info delay
  - QUESTION contains all required fields
  - trivia_question formatted correctly
  - short_question is solvable

- **Test ANSWER Message**
  - Client sends ANSWER
  - Server validates answer
  - Server updates score for correct answers

- **Test RESULT Message**
  - Server sends RESULT with correct/feedback
  - Feedback uses config strings
  - Answer substitution works ({answer}, {correct_answer})

- **Test LEADERBOARD Message**
  - Server sends after question timeout or all answers
  - Leaderboard sorted by score (descending)
  - Ties broken lexicographically
  - Same rank for tied players
  - Correct singular/plural point nouns

- **Test FINISHED Message**
  - Server sends after all questions
  - Final standings formatted correctly
  - Winner announcement (one_winner vs multiple_winners)
  - Server disconnects clients after

- **Test BYE Message**
  - Client can disconnect anytime
  - Player remains in game (score frozen)
  - Leaderboard includes disconnected players

#### Timing Tests
- **Test Question Timeout**
  - Question times out after question_seconds
  - LEADERBOARD sent after timeout
  - Unanswered question doesn't increase score

- **Test Question Interval**
  - Correct delay between questions
  - Correct delay before first question (READY)

#### Client Mode Tests
- **Test Manual Mode ("you")**
  - Client accepts stdin input
  - Client sends input as ANSWER
  - Timeout aborts waiting for input

- **Test Auto Mode ("auto")**
  - Client solves Mathematics correctly
  - Client solves Roman Numerals correctly
  - Client solves IP questions correctly
  - Client solves Network/Broadcast correctly
  - 100% accuracy achieved

- **Test AI Mode ("ai")**
  - Client connects to Ollama API
  - Client sends prompt to /api/chat
  - Client forwards LLM response unmodified
  - Config validation (ollama_config required)

### 3. System Tests (End-to-End)
Test complete game scenarios.

#### Single Player Game
- Connect → HI → READY → QUESTION → ANSWER → RESULT → LEADERBOARD → repeat → FINISHED

#### Multi-Player Game
- 2+ players connect
- All receive READY simultaneously
- All receive same QUESTION
- Different answers give different RESULTs
- LEADERBOARD shows all players
- FINISHED shows final rankings

#### Complete Auto-Mode Game
- Auto client plays full game
- Gets 100% correct answers
- Wins game

#### Player Disconnection Scenarios
- Player disconnects before game starts
- Player sends BYE during question
- Player disconnects after answering
- Disconnected player in final standings

### 4. Error Handling Tests

#### Server Errors
- Missing --config argument → error message + exit 1
- Non-existent config file → error message + exit 1
- Port already in use → binding error + exit 1

#### Client Errors
- Missing --config argument → error message + exit 1
- Non-existent config file → error message + exit 1
- Missing ollama_config in ai mode → error message + exit 1
- Connection failed → "Connection failed" message, continue running

### 5. Edge Case Tests

#### Leaderboard Edge Cases
- All players tied at 0 points
- All players tied with same score
- 3-way tie for first place
- Lexicographic tie-breaking

#### Answer Validation
- Exact match required (case-sensitive)
- No partial credit
- String comparison only

#### Configuration Substitution
- Test {question_interval_seconds} in ready_info
- Test {answer} and {correct_answer} in feedback
- Test other config substitutions

## Test Implementation Strategy

### Bash Tests (using nc/ncat)
- Good for: Protocol testing, server behavior
- Use existing run_tests_nc.sh as base
- Add more comprehensive scenarios

### Python Tests (using unittest/socket)
- Good for: Unit tests, question solving, integration tests
- Can simulate clients programmatically
- Better control over timing and concurrency

### Hybrid Approach
- Python test harness that:
  1. Starts server in subprocess
  2. Creates client connections
  3. Sends messages
  4. Validates responses
  5. Cleans up

## Coverage Goals

To get full marks, ensure:
1. ✅ Tests are functional and automatically runnable
2. ✅ Tests properly use networking (real socket connections)
3. ✅ Wide coverage of both client and server behaviors
4. ✅ At least one complete end-to-end game test
5. ✅ Clear test organization and documentation

## Recommended Test Files Structure

```
tests/
├── unit/
│   ├── test_questions.py          # Question generation/solving
│   ├── test_message_encoding.py   # JSON encoding/decoding
│   └── test_config_loading.py     # Config file handling
├── integration/
│   ├── test_protocol.py            # Message exchange
│   ├── test_client_modes.py        # Manual/auto/ai modes
│   └── test_timing.py              # Timeouts and intervals
├── system/
│   ├── test_single_player.py       # Complete 1-player game
│   ├── test_multi_player.py        # Complete 2+ player game
│   └── test_disconnection.py       # Disconnect scenarios
├── bash/
│   ├── test_server_nc.sh           # Server tests with nc
│   └── test_client_output.sh       # Client output validation
└── configs/
    ├── test_*.json                 # Various test configurations
```

## Test Execution

### Run All Tests
```bash
python -m pytest tests/
```

### Run Specific Category
```bash
python -m pytest tests/unit/
python -m pytest tests/integration/
```

### Run Bash Tests
```bash
bash tests/bash/test_server_nc.sh
```

## Notes

- Assignment only requires testing with 1 client for full marks
- Can test with multiple clients for bonus learning
- Staff test cases use different questions.py (randomness not tested)
- Focus on protocol correctness and behavior, not specific question content
