import pyautogui
import time
from time import sleep, time
from threading import Event
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

#region Global Variables
global repeat_macro
repeat_macro = False

global repeat_macro_delay
repeat_macro_delay = 1.00

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

global use_multiple
use_multiple = False

global random_multiple
random_multiple = False

global held_keys
held_keys = list()

global held_clicks
held_clicks = list()

global executed_actions
executed_actions = list()

global macroList
macroList = list()
#endregion

def main():

    print("ZyMacro - Playback")

    # Input options here

    #region CLI Options
    parser = argparse.ArgumentParser(
        prog='Zy Macro - Playback',
        description='Macro Playback',
        epilog='')

    parser.add_argument('-p', '--path', help="Path to macro file", required=False)
    parser.add_argument('-k', '--hotkey', help="Hotkey to toggle playback", required=False)
    parser.add_argument('-kk', '--pause', help="Hotkey to toggle pause", required=False)
    parser.add_argument('-r', '--repeat', action='store_true', default=False, help="Repeat macro for duration", required=False)
    parser.add_argument('-rrd', '--repeatrandomdelay', action='store_true', default=False, help="Delay between macro instances are random : scaled with -rd", required=False)
    parser.add_argument('-rd', '--repeatdelay', type=float, help="Length of delay between macro instances", required=False)
    parser.add_argument('-d', '--duration', type=float, help="Duration of repeat macro operation", required=False)
    parser.add_argument('-sd', '--startdelay', type=int, help="Length of delay before start of operation", required=False)
    parser.add_argument('-m', '--multiple', action='store_true', default=False, help="Use multiple macro scripts interchangeably", required=False)
    parser.add_argument('-mr', '--multiplerandom', action='store_true', default=False, help="Length of delay before start of operation", required=False)

    global args
    args = parser.parse_args()

    global MACRO_FILE
    try:
        if args.path is not None:
            MACRO_FILE = args.path
    except:
        None

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

    global use_multiple
    try:
        if args.multiple is not None:
            use_multiple = args.multiple
    except:
        None

    global random_multiple
    try:
        if args.multiplerandom is not None:
            random_multiple = args.multiplerandom
    except:
        None

    if random_multiple == True:
        use_multiple = True

    global macroList
    global filepath

    if use_multiple:

        if args.path is None:
            filepath = filepath = "..\\zymacro\\input\\"
        else:
            filepath = args.path

        # Credit: https://pythonguides.com/python-get-all-files-in-directory/
        for root, dirs, files in os.walk(filepath):
            for file in files:
                macroList.append(os.path.join(root,file))

        if random_multiple and len(macroList)-1 > 0:
            filepath = macroList[random.randrange(0,len(macroList)-1)]
        else:
            filepath = macroList[0]

        macros_used = ""

        for path in macroList:
            macros_used += os.path.abspath(path)
            if path != macroList[len(macroList)-1]:
                macros_used += ", "

        print("Using macros: {}".format(macros_used))

    else:
        print("Using macro: {}".format(MACRO_FILE))

    print("Settings: Start Delay - {} | Duration - {} | Repeat - {} | Repeat Delay - {} | Repeat Random Delay - {} | Multiple Macros - {} | Random Multiple - {}"
        .format(macro_start_delay, macro_duration, repeat_macro, repeat_macro_delay, repeat_macro_random_delay, use_multiple, random_multiple))
    #endregion

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
    global macroList

    global filepath

    global args

    if repeat_macro:
        print("Starting iteration {}...".format(i))

    #region Get filepath
    
#    if use_multiple and i == 0:

#        if args.path is None:
#            filepath = filepath = "..\\zymacro\\input\\"
#        else:
#            filepath = filename

        # Credit: https://pythonguides.com/python-get-all-files-in-directory/
#        for root, dirs, files in os.walk(filepath):
#            for file in files:
#                macroList.append(os.path.join(root,file))

#        if random_multiple:
#            filepath = macroList[random.randrange(0,len(macroList)-1)]
#        else:
#            filepath = macroList[0]

    if use_multiple and len(macroList) > 1:

        if random_multiple:
            filepath = macroList[random.randrange(0,len(macroList)-1)]
        else:
            filepath = macroList[i%len(macroList)]
        
    elif not use_multiple:
        
        if args.path is None:
            #script_dir = os.path.abspath(os.path.dirname(__file__))
            #script_dir = script_dir.replace("\\code\\record", "")
            filepath = "..\\zymacro\\input\\" + filename

    #        script_dir = os.path.dirname(__file__)
    #        filepath = os.path.join(
    #            script_dir,
    #            '',
    #            filename
    #        )

        else:
            filepath = filename

    elif use_multiple and len(macroList) == 1:
        filepath = macroList[0]

    if filepath == "" or filepath == None:
        raise Exception("No file path specified for macro input!")
    #endregion

    print("Running macro: {} ...".format(filepath))

    # Read the file
    with open(filepath, 'r') as jsonFile:

        # Parse the json
        global data
        data = simplejson.load(jsonFile)

        global timerIndex
        global iteratorIndex
        timerIndex = 0
        iteratorIndex = 0

        #Credits: https://stackoverflow.com/questions/2846653/how-can-i-use-threading-in-python?rq=1

        #global waitForTimestamp
        #global waitForNextAction
        #global waitForCurrentAction

        #waitForTimestamp = False
        #waitForNextAction = False
        #waitForCurrentAction = False

        #pool = mp.Pool(4)
        #pool.map(actionTimer, range(0, len(data)))

        #pool2 = mp.Pool(4) # No. of threads
        #pool2.map(actionIterator, range(0, len(data)))

        #pool.start()
        #pool2.start()

        #pool.wait()
        #pool2.wait()

        #pool.join()
        #pool2.join()

        actionPool = mp.Pool(2)
        actionPool.map(actionPlayer, range(0, len(data)))
        actionPool.close()
        actionPool.terminate()
        actionPool.join()

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

def actionPlayer(index): # Old Player
    
    global data

    action = data[index]
    
    print("---")
    print("Initializing Action...")
    
    global executed_actions
    if executed_actions.__contains__(action):
        return
    else:
        executed_actions.append(action)

    if Decimal(elapsed_time()) < Decimal(action['time']):
        sleep(float(Decimal(action['time']) - Decimal(elapsed_time())))

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

    global action_start_time
    action_start_time = Decimal(time())

    # Look for esc input to exit
    if action['button'] == 'Key.esc':
        return

    #region Perform action
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
    #endregion

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

def actionTimer(index): # Use with actionIterator to time actions according to macro.json

    global data

    action = data[index]

    global waitForTimestamp
    global waitForNextAction
    global waitForCurrentAction

    if Decimal(elapsed_time()) < Decimal(action['time']):
        sleep(float(Decimal(action['time']) - Decimal(elapsed_time())))

    print("Initializing Action...")
    
    waitForTimestamp = True
    while not waitForCurrentAction:
        None
    
    try:
        next_action = data[index+1]
    except IndexError:
        return

    action_time = Decimal(Decimal(next_action['time']) - Decimal(action['time']))

    if action_time < 0:
        raise Exception('Unexpected action order')

    global action_start_time
    action_time -= Decimal(Decimal(time()) - Decimal(action_start_time))

    if action_time < 0:
        action_time = 0
    
#            if action_time >= 1:

    print("Sleeping for {}".format(round(action_time, 5)))

    sleep(float(action_time))

    waitForNextAction = True

    global timerIndex
    timerIndex += 1

    waitForTimestamp = False
    waitForCurrentAction = False
    waitForNextAction = False

def actionIterator(index): # Using multithreading function to increase accuracy of playback by eliminating queue

    global data

    global waitForTimestamp
    global waitForNextAction
    global waitForCurrentAction

#    if index >= len(data):
#        return

    action = data[index]

    global executed_actions
    if executed_actions.__contains__(action):
        return
    else:
        executed_actions.append(action)

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

    global action_start_time
    action_start_time = Decimal(time())

    while not waitForTimestamp:
        None

    global timerIndex
    global iteratorIndex

    if not timerIndex == iteratorIndex:
        raise Exception("actionTimer & actionIterator out of sync!")

#    if Decimal(elapsed_time()) < Decimal(action['time']):
#        sleep(float(Decimal(action['time']) - Decimal(elapsed_time())))

#    while Decimal(elapsed_time()) < Decimal(action['time']):
#        None

    # Look for esc input to exit
    if action['button'] == 'Key.esc':
        return

    #region Perform action
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
    #endregion

    waitForCurrentAction = True

    while not waitForNextAction:
        None

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