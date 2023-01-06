import pyautogui
import time
from time import sleep, time
import os
import json
import simplejson
import math, random
import argparse
from pynput import mouse, keyboard
import threading
import pydirectinput
from decimal import Decimal
import multiprocessing.dummy as mp

# from recorder import elapsed_time

global repeat_macro
repeat_macro = False

global repeat_macro_delay
repeat_macro_delay = 0.00

global repeat_macro_random_delay
repeat_macro_random_delay = False

global macro_duration
macro_duration = 30.00

global macro_start_delay
macro_start_delay = int(5)

global MACRO_FILE
MACRO_FILE = "macro.json"

global TOGGLE_PAUSE
TOGGLE_PAUSE = keyboard.Key.pause

global paused
paused = False

global TOGGLE_PLAYBACK
TOGGLE_PLAYBACK = keyboard.Key.esc

global start_time
start_time = Decimal(0)

global operation_halted
operation_halted = False

global operation_stopped
operation_stopped = False

global held_keys
held_keys = list()

global held_clicks
held_clicks = list()

global executed_actions
executed_actions = list()

def main():

    print("ZyMacro - Playback")

    # Input options here
    # CLI Features
    parser = argparse.ArgumentParser(
        prog='Zy Macro - Playback',
        description='Macro Playback',
        epilog='')

    parser.add_argument('-p', '--path', help="Path to macro file", required=False)
    parser.add_argument('-k', '--hotkey', help="Hotkey to toggle playback", required=False)
    parser.add_argument('-kk', '--pause', help="Hotkey to toggle pause", required=False)
    parser.add_argument('-r', '--repeat', type=bool, help="Repeat macro for duration", required=False)
    parser.add_argument('-rrd', '--repeatrandomdelay', type=bool, help="Delay between macro instances are random : scaled with -rd", required=False)
    parser.add_argument('-rd', '--repeatdelay', type=float, help="Length of delay between macro instances", required=False)
    parser.add_argument('-d', '--duration', type=float, help="Duration of repeat macro operation", required=False)
    parser.add_argument('-sd', '--startdelay', type=int, help="Length of delay before start of operation", required=False)

    global args
    args = parser.parse_args()

    global MACRO_FILE
    try:
        if args.path is not None:
            MACRO_FILE = args.path
    except:
        None

    print("Using macro: {}".format(MACRO_FILE))

    global macro_start_delay
    try:
        if args.startdelay is not None:
            macro_start_delay = args.startdelay
    except:
        None
    
    global macro_duration
    try:
        if args.duration is not None:
            macro_duration = args.duration
    except:
        None

    global repeat_macro
    try:
        if args.repeat is not None:
            repeat_macro = args.repeat
    except:
        None

    global repeat_macro_delay
    try:
        if args.repeatdelay is not None:
            repeat_macro_delay = args.repeatdelay
    except:
        None

    global repeat_macro_random_delay
    try:
        if args.repeatrandomdelay is not None:
            repeat_macro_random_delay = args.repeatrandomdelay
    except:
        None

    print("Settings: Start Delay - {} | Duration - {} | Repeat - {} | Repeat Delay - {} | Repeat Random Delay - {}"
        .format(macro_start_delay, macro_duration, repeat_macro, repeat_macro_delay, repeat_macro_random_delay))

    global TOGGLE_PLAYBACK
    try:
        if args.hotkey is not None:
            TOGGLE_PLAYBACK = args.hotkey
    except:
        None

    print("Setup complete, awaiting key input - {}".format(TOGGLE_PLAYBACK.name))

    global TOGGLE_PAUSE
    try:
        if args.pause is not None:
            TOGGLE_PAUSE = args.pause
    except:
        None

    print("To toggle pause use - {}".format(TOGGLE_PAUSE.name))

    with keyboard.Listener(on_release=start_playback) as listener:
        listener.join()

    print("Initializing playback...")

    initializePyAutoGUI()
    countdownTimer()

    global start_time
    start_time = time()

    t1 = threading.Thread(target=toggle_check)
    t1.start()

    #global t2

    #t2 = threading.Thread(target=playActions, args=MACRO_FILE)
    #t2.daemon = True
    #t2.start()

    # Wait until thread playing actions concludes
    #t2.join()

    global operation_halted

    if not operation_halted and elapsed_time() < macro_duration:
        playActions(MACRO_FILE)

    if operation_halted:
        print("Halting Macro Operation...")
        sleep(2.0)
        print("Macro Operation Stopped Unexpectedly")
    else:
        sleep(2.00)
        print("Macro Operation Successfully Executed")
        operation_halted = True
    
    global operation_stopped
    operation_stopped = True
    #raise keyboard.Listener.StopException

def start_playback(key):
    if key == TOGGLE_PLAYBACK:
        raise keyboard.Listener.StopException

def toggle_check():

    global macro_duration

    if elapsed_time() < macro_duration:
        with keyboard.Listener(on_release=key_release) as listener:
            listener.join()
    
    #operation_halted = True
    #raise keyboard.Listener.StopException

def key_release(key):
    global operation_halted
    global t2
    global paused
    if key == TOGGLE_PLAYBACK:
        operation_halted = True
        #print("Halt key pressed...")
        #sleep(1.0)
        #print("Halting Macro Operation...")
        #sleep(2.0)
        #print("Macro Operation Stopped Unexpectedly")
        #exit()
        #quit()
        raise keyboard.Listener.StopException
    elif key == TOGGLE_PAUSE:

        if paused:
            for key in held_keys:
                    pydirectinput.keyUp(key)
            for click in held_clicks:
                pydirectinput.mouseUp(click)

        paused = not paused


def elapsed_time():
    global start_time
    return Decimal(Decimal(time()) - Decimal(start_time))

def initializePyAutoGUI():

    # Timer
    print("Initializing PyAutoGUI", end="", flush=True)

    for i in range(0,2):
        print(".", end="", flush=True)
        sleep(1)

    print ("Initialized")

def countdownTimer():
    # Macro start delay
    print("Starting", end="", flush=True)
    for i in range(1, macro_start_delay):
        print(".", end="", flush=True)
        sleep(1)
    print("Macro Initialized")

def playActions(filename, i=0):
    
    global operation_halted
    global paused
    global held_keys

    # Read the file
    global args
    if args.path is None:
        script_dir = os.path.abspath(os.path.dirname(__file__))
        script_dir = script_dir.replace("\\code\\record", "")
        filepath = "..\\zymacro\\input\\" + filename

#        script_dir = os.path.dirname(__file__)
#        filepath = os.path.join(
#            script_dir,
#            '',
#            filename
#        )

    else:
        filepath = filename

    if repeat_macro:
        print("Starting iteration {}...".format(i))

    with open(filepath, 'r') as jsonFile:

        # Parse the json
        global data
        data = simplejson.load(jsonFile)

        pool = mp.Pool(6) # No. of threads
        pool.map(actionIterator, range(0, len(data)))
        pool.close()
        pool.join()

    if repeat_macro:

        executed_actions.clear()

        if Decimal(elapsed_time()) > macro_duration:
            print("Reached duration specified...")
        elif operation_halted:
            print("Halting Macro Operation...")
            sleep(1.0)
            print("Macro Operation Stopped Unexpectedly")
            global operation_stopped
            operation_stopped = True
        else:
            if repeat_macro_random_delay:
                randomdelay = repeat_macro_delay * random()
                print("Delaying for {}".format(randomdelay))
                sleep(randomdelay)
                playActions(filename, i+1)
            else:
                print("Delaying for {}".format(repeat_macro_delay))
                sleep(repeat_macro_delay)
                playActions(filename, i+1)

def actionIterator(iterations): # Using multithreading function to increase accuracy of playback by eliminating queue

    global data
    index = iterations

#    if index >= len(data):
#        return

    action = data[index]

    global executed_actions
    if executed_actions.__contains__(action):
        return
    else:
        executed_actions.append(action)

    if Decimal(elapsed_time()) < Decimal(action['time']):
        sleep(float(Decimal(action['time']) - Decimal(elapsed_time())))

#    while Decimal(elapsed_time()) < Decimal(action['time']):
#        None

    if operation_halted:
        return
    elif paused:
        print("Macro Operation Paused")
        for key in held_keys:
            pydirectinput.keyUp(key)
        for click in held_clicks:
            pydirectinput.mouseUp(click)
        while paused:
            if operation_halted:
                break

    action_start_time = Decimal(time())

    # Look for esc input to exit
    if action['button'] == 'Key.esc':
        return

    # Perform action
    if action['type'] == 'keyDown':
        key = convertKey(action['button'])
        #pyautogui.keyDown(key)
        pydirectinput.keyDown(key)
        if not held_keys.__contains__(key):
            held_keys.append(key)
        print("keyDown on {}".format(key))
    elif action['type'] == 'keyUp':
        key = convertKey(action['button'])
        #pyautogui.keyUp(key)
        pydirectinput.keyUp(key)
        if held_keys.__contains__(key):
            held_keys.remove(key)
        print("keyUp on {}".format(key))
    elif action['type'] == 'clickDown':
        #pyautogui.click(action['pos'][0], action['pos'][1], duration=0.25)
        #pydirectinput.click(action['pos'][0], action['pos'][1], duration=0.25)
        click = convertClick(action['button'])
        pydirectinput.mouseDown(action['pos'][0], action['pos'][1], button=click)
        if not held_clicks.__contains__(click):
            held_clicks.append(click)
        print("clickDown on {}".format(click))
    elif action['type'] == 'clickUp':
        click = convertClick(action['button'])
        pydirectinput.mouseUp(action['pos'][0], action['pos'][1], button=click)
        if held_clicks.__contains__(click):
            held_clicks.remove(click)
        print("clickUp on {}".format(click))

    try:
        next_action = data[index+1]
    except IndexError:
        return

    action_time = Decimal(Decimal(next_action['time']) - Decimal(action['time']))

    if action_time < 0:
        raise Exception('Unexpected action order')

    action_time -= Decimal(Decimal(time()) - Decimal(action_start_time))

    if action_time < 0:
        action_time = 0
    
#            if action_time >= 1:
    print("Sleeping for {}".format(round(action_time, 5)))

    sleep(float(action_time))

def convertKey(button):

    PYNPUT_SPECIAL_CASE_MAP = {
        'alt_l': 'altleft',
        'alt_r': 'altright',
        'alt_gr': 'altright',
        'caps_lock': 'capslock',
        'ctrl_l': 'ctrlleft',
        'ctrl_r': 'ctrlright',
        'page_down': 'pagedown',
        'page_up': 'pageup',
        'shift_l': 'shiftl',
        'shift_r': 'shiftright',
        'num_lock': 'numlock',
        'print_screen': 'printscreen',
        'scroll_lock': 'scrolllock'
    }

    blank_key = button.replace('Key.', '')

    if blank_key in PYNPUT_SPECIAL_CASE_MAP:
        return PYNPUT_SPECIAL_CASE_MAP[blank_key]

    return blank_key

def convertClick(button):
    blank_button = button.replace('Button.', '')
    return blank_button

if __name__ == "__main__" and not operation_stopped:
    main()
else:
    quit()