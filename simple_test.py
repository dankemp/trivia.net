#!/usr/bin/env python3
"""
Simple test to verify server works
Run this while server is running
"""

import socket
import json
import sys


def test_server():
    try:
        # Connect
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 7778))
        print("✓ Connected to server")

        # Send HI
        hi_msg = json.dumps({"message_type": "HI", "username": "TestPlayer"})
        sock.sendall((hi_msg + '\n').encode('utf-8'))
        print(f"✓ Sent: {hi_msg}")

        # Receive response (newline delimited)
        data = b""
        while True:
            chunk = sock.recv(1)
            if not chunk:
                break
            data += chunk
            if chunk == b'\n':
                break

        if data:
            response = json.loads(data.decode('utf-8').strip())
            print(f"✓ Received: {response}")

            if response.get("message_type") == "READY":
                print("✓✓✓ TEST PASSED - Server sent READY message!")
                return True
            else:
                print(f"✗ Wrong message type: {response.get('message_type')}")
                return False
        else:
            print("✗ No response from server")
            return False

    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    finally:
        sock.close()


if __name__ == "__main__":
    success = test_server()
    sys.exit(0 if success else 1)