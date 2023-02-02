from pynput import mouse, keyboard
from time import time
from threading import Event
import math
import json
import os
import argparse
import simplejson
from decimal import Decimal

#region Global Variables
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
#endregion

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

    global DEFAULT_FILENAME
    try:
        if args.name is not None:
            OUTPUT_FILENAME = args.name
        else:
            OUTPUT_FILENAME = DEFAULT_FILENAME
    except:
        OUTPUT_FILENAME = DEFAULT_FILENAME

    OUTPUT_FILENAME = file_rename("..\\zymacro\\output\\", OUTPUT_FILENAME)
    
    filepath = "..\\zymacro\\output\\" + '{}.json'.format(OUTPUT_FILENAME)
    
    print("Output file name: {}".format(os.path.abspath(filepath)))

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

    with open(filepath, 'w') as outfile:
        simplejson.dump(input_events, outfile, indent=4)

    print("Saved macro at - {}".format(os.path.abspath(filepath)))

def file_rename(filepath = str, edit_name = str): # Output file rename in the case of identical file name detected in path

    if os.path.exists(os.path.abspath(filepath + '{}.json'.format(edit_name))):

        if not (edit_name.__contains__('_') and str(edit_name[len(edit_name)-1]).isdigit()):
            edit_name += '_1'

        i = 0
        j = 1

        while i < j:

            suffix_index = len(edit_name)-1

            k = 0
            l = 1

            while k < l:
                if str(edit_name[len(edit_name)-1-k]).isdigit():
                    k += 1
                    l += 1
                    suffix_index -= 1
                elif str(edit_name[len(edit_name)-1-k]) == '_':
                    k += 1
                else:
                    raise Exception("Suffix format is invalid")

            edit_name = edit_name.replace(edit_name[suffix_index], '_{}'.format(i.__index__()))

            if os.path.exists(os.path.abspath("..\\zymacro\\output\\" + '{}.json'.format(edit_name))):
                i += 1
                j += 1
            else:
                i += 1
                
        return edit_name

    else:
        return edit_name

def start_recording(key):
    global keyboard_listener
    global keyboard_listener2
    if key == RECORD_HOTKEY:
        raise keyboard.Listener.StopException

def end_recording(key):

    if key == RECORD_HOTKEY:

        # Prevents start key press from ending record session prematurely
        if elapsed_time() < 0.5:
            return

        # Stop mouse_listener
        global mouse_listener
        #global mouse_listener2
        global keyboard_listener
        global keyboard_listener2
        mouse_listener.stop()
        #mouse_listener2.stop()
        # Stop keyboard.Listener
        keyboard.Listener.stop(keyboard_listener)
        keyboard.Listener.stop(keyboard_listener2)

def elapsed_time():
    global start_time
    return Decimal(Decimal(time()) - Decimal(start_time))

def record_event(event_type, event_time, button, pos=None):

    global input_events

    if button != RECORD_HOTKEY:

        if input_events.__contains__({
            'time': event_time,
            'type': event_type,
            'button': str(button),
            'pos': pos
        }):
            return

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

def on_click(x, y, button, pressed):

    global unreleased_clicks

    #if button in unreleased_clicks and pressed:
        #return
    #elif not button in unreleased_clicks and pressed:
    if pressed:
        #unreleased_clicks.append(button)
        record_event(EventType.CLICKDOWN, elapsed_time(), button, (x, y))
    else:
        record_event(EventType.CLICKUP, elapsed_time(), button, (x, y))
        #unreleased_clicks.remove(button)

def on_click_release(x, y, button):

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
    #global mouse_listener2
    mouse_listener = mouse.Listener(on_click=on_click)
    #mouse_listener2 = mouse.Listener()

    #with mouse.Listener(on_click=on_click) as listener:
        #mouse_listener = listener.join()

    mouse_listener.start()
    #mouse_listener2.start()
    # Wait for Listener to be ready
    mouse_listener.wait()
    #mouse_listener2.wait()

    global start_time
    global keyboard_listener, keyboard_listener2
    keyboard_listener = keyboard.Listener(on_press=on_press)
    keyboard_listener2 = keyboard.Listener(on_release=on_release)

    keyboard_listener.start()
    keyboard_listener2.start()

    keyboard_listener.wait()
    keyboard_listener2.wait()

    end_listener = keyboard.Listener(on_release=end_recording)
    end_listener.start()
    end_listener.wait()

    print("Recording Started")
    
    start_time = time()

    keyboard_listener.join()
    keyboard_listener2.join()
    mouse_listener.join()
    #mouse_listener2.join()

if __name__ == "__main__":
    main()