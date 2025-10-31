#!/usr/bin/env python3
"""
Test script for session notification system.
Run this to verify notification and audio are working.
"""
import json
from pathlib import Path
import subprocess
import sys

# Import the functions from session_notification
sys.path.insert(0, str(Path(__file__).parent))
from session_notification import (
    get_conversation_file,
    get_citizen_name,
    get_sound_path,
    extract_last_lines,
    show_notification
)

def main():
    print("=== Testing Session Notification System ===\n")

    # 1. Test conversation file detection
    print("1. Finding conversation file...")
    conv_file = get_conversation_file()
    if conv_file:
        print(f"   ✓ Found: {conv_file}")
    else:
        print("   ✗ No conversation file found")
        return

    # 2. Test citizen name detection
    print("\n2. Detecting citizen name...")
    citizen = get_citizen_name()
    print(f"   ✓ Citizen: {citizen}")

    # 3. Test sound path detection
    print("\n3. Finding voice file...")
    sound_path = get_sound_path(citizen)
    print(f"   ✓ Sound: {sound_path}")
    print(f"   ✓ Exists: {Path(sound_path).exists()}")

    # 4. Test conversation parsing
    print("\n4. Parsing conversation...")
    try:
        with open(conv_file, 'r') as f:
            data = json.load(f)

        messages = data.get('messages', [])
        print(f"   ✓ Total messages: {len(messages)}")

        # Find last assistant message
        assistant_messages = [m for m in messages if m.get('role') == 'assistant']
        if assistant_messages:
            last_msg = assistant_messages[-1]
            content = last_msg.get('content', '')
            last_lines = extract_last_lines(content, num_lines=2)
            print(f"   ✓ Last assistant message preview:")
            print(f"     '{last_lines[:100]}...'")
        else:
            print("   ✗ No assistant messages found")
            return
    except Exception as e:
        print(f"   ✗ Error parsing: {e}")
        return

    # 5. Test audio playback
    print("\n5. Testing audio playback...")
    try:
        result = subprocess.run(['mpg123', '--version'],
                              capture_output=True, text=True, timeout=2)
        print(f"   ✓ mpg123 installed: {result.stdout.split()[1] if result.stdout else 'yes'}")

        # Try to play the sound
        print(f"   → Attempting to play: {Path(sound_path).name}")
        subprocess.run(['mpg123', '-q', sound_path],
                      timeout=5,
                      stderr=subprocess.DEVNULL)
        print("   ✓ Audio playback completed")
    except FileNotFoundError:
        print("   ✗ mpg123 not found")
    except subprocess.TimeoutExpired:
        print("   ⚠ Audio playback timed out")
    except Exception as e:
        print(f"   ✗ Audio error: {e}")

    # 6. Test Windows notification
    print("\n6. Testing Windows notification...")
    print("   → Attempting to show Windows toast notification...")
    try:
        show_notification(citizen, last_lines)
        print("   ✓ Notification command sent (check Windows for toast)")
    except Exception as e:
        print(f"   ✗ Notification error: {e}")

    print("\n=== Test Complete ===")
    print("\nIf you didn't see/hear:")
    print("  - Windows toast notification with citizen name and message")
    print("  - Voice saying: 'Bridge holds. What's next?'")
    print("\nThen check:")
    print("  1. Windows notification settings (make sure they're enabled)")
    print("  2. Volume/speakers (make sure WSL can access Windows audio)")
    print("  3. WSL2 version (newer versions have better audio support)")

if __name__ == '__main__':
    main()
