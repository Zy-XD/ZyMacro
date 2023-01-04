from pynput import mouse, keyboard
from time import time
import math
import json
import os
import argparse
import simplejson
from decimal import Decimal

global RECORD_HOTKEY
DEFAULT_HOTKEY = keyboard.Key.esc

DEFAULT_FILENAME = "macro"

# Declare mouse_listener globally - on_release stops it
mouse_listener = None

# Declare start_time globally - callback functions reference it
start_time = None

# Track unreleased keys to prevent press event spam
unreleased_keys = list()

unreleased_clicks = list()

# Input event storage
input_events = list()

operation_completed = False

start_time = Decimal(0)

class EventType():
    KEYDOWN = 'keyDown'
    KEYUP = 'keyUp'
    CLICKUP = 'clickUp'
    CLICKDOWN = 'clickDown'

def main():

    print("ZyMacro - Recorder")

    # Input options here
    # CLI Features
    parser = argparse.ArgumentParser(
        prog='Zy Macro - Recorder',
        description='Macro Recorder',
        epilog='')

    parser.add_argument('-n', '--name', help="Name of output file", required=False)
    parser.add_argument('-k', '--hotkey', help="Hotkey used to toggle recorder", required=False)
    args = parser.parse_args()

    try:
        if args.name is not None:
            OUTPUT_FILENAME = args.name
        else:
            OUTPUT_FILENAME = DEFAULT_FILENAME
    except:
        OUTPUT_FILENAME = DEFAULT_FILENAME
    
    print("Output file name: {}".format(OUTPUT_FILENAME))

    global RECORD_HOTKEY
    try:
        if args.hotkey is not None:
            RECORD_HOTKEY = args.hotkey
        else:
            RECORD_HOTKEY = DEFAULT_HOTKEY
    except:
        RECORD_HOTKEY = DEFAULT_HOTKEY

    # Wait until hotkey to start macro recording
    print("Press - {} - to start recording".format(RECORD_HOTKEY.name))
    with keyboard.Listener(on_release=start_recording) as listener:
        listener.join()

    print("Starting recording")
    runListeners()
    
    print("Recorded: {} secs".format(round(elapsed_time(), 5)))

    global input_events

    print("")
    print(simplejson.dumps(input_events))

    # Write output to a file
    script_dir = os.path.abspath(os.path.dirname(__file__))
    
    script_dir = script_dir.replace("\\code\\record", "")

    filepath = "..\\zymacro\\output\\" + '{}.json'.format(OUTPUT_FILENAME)
    with open(filepath, 'w') as outfile:
        simplejson.dump(input_events, outfile, indent=4)

    print("Saved macro at - {}".format(os.path.abspath(filepath)))

def start_recording(key):
    if key == RECORD_HOTKEY:
        raise keyboard.Listener.StopException

def elapsed_time():
    global start_time
    return Decimal(Decimal(time()) - Decimal(start_time))

def record_event(event_type, event_time, button, pos=None):

    global input_events

    if button != RECORD_HOTKEY:

        input_events.append({
            'time': event_time,
            'type': event_type,
            'button': str(button),
            'pos': pos
        })

        if event_type == EventType.CLICKUP:
            print("{} on {} pos {} at {} secs".format(event_type, button, pos, round(event_time, 5)))
        elif event_type == EventType.CLICKDOWN:
            print("{} on {} pos {} at {} secs".format(event_type, button, pos, round(event_time, 5)))
        else:
            print("{} on {} at {} secs".format(event_type, button, round(event_time, 5)))

def on_press(key):

    global unreleased_keys

    if key in unreleased_keys:
        return
    else:
        unreleased_keys.append(key)

    try:
        record_event(EventType.KEYDOWN, elapsed_time(), key.char)
    except AttributeError:
        record_event(EventType.KEYDOWN, elapsed_time(), key)

def on_release(key):

    global unreleased_keys

    try:
        unreleased_keys.remove(key)
    except ValueError:
        print("Error: {} not valid - Not in unreleased_keys".format(key))
    
    try:
        record_event(EventType.KEYUP, elapsed_time(), key.char)
    except AttributeError:
        record_event(EventType.KEYUP, elapsed_time(), key)
    
    if key == RECORD_HOTKEY:
        # Stop mouse_listener
        global mouse_listener
        mouse_listener.stop()
        # Stop keyboard.Listener
        raise keyboard.Listener.StopException

def on_click(x, y, button, pressed):

    global unreleased_clicks

    if button in unreleased_clicks:
        return
    else:
       unreleased_clicks.append(button)

    if pressed:
        record_event(EventType.CLICKDOWN, elapsed_time(), button, (x, y))
    else:
        record_event(EventType.CLICKUP, elapsed_time(), button, (x, y))

def on_click_release(x, y, button, pressed):

    global unreleased_clicks

    try:
        unreleased_clicks.remove(button)
    except ValueError:
        print("Error: {} not valid - Not in unreleased_clicks".format(button))
        
    try:
        record_event(EventType.CLICKUP, elapsed_time(), button, (x, y))
    except AttributeError:
        record_event(EventType.CLICKUP, elapsed_time(), button, (x, y))

def runListeners():
    
    # Collect mouse input events
    global mouse_listener
    mouse_listener = mouse.Listener(on_click=on_click, on_release=on_click_release)
    mouse_listener.start()
    # Wait for Listener to be ready
    mouse_listener.wait()

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        global start_time
        start_time = time()
        listener.join()

if __name__ == "__main__":
    main()