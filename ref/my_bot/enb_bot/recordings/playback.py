import pyautogui
import time
from time import sleep, time
import os
import json


def main():
    initializePyAutoGUI()
    countdownTimer()

    playActions("write.json")
    sleep(2.00)

    print("Execution success")

def initializePyAutoGUI():
    pyautogui.FAILSAFE = True


def countdownTimer():
    # timer
    print("Starting", end="", flush=True)
    for i in range(0, 10):
        print(".", end="", flush=True)
        sleep(1)
    print("Go")    

def playActions(filename):
    # Read the file
    scrip_dir = os.path.dirname(__file__)
    filepath = os.path.join(
        scrip_dir,
        '',
        filename
    )
    with open(filepath, 'r') as jsonfile:
        # parse the json
        data = json.load(jsonfile)

        for index, action in enumerate(data):
            action_start_time = time()

            # look for escape input to exit
            if action['button'] == 'Key.esc':
                break

            # perform the action
            if action['type'] == 'keyDown':
                key = convertKey(action['button'])
                pyautogui.keyDown(key)
                print("keyDown on {}".format(key))
            elif action['type'] == 'keyUp':
                key = convertKey(action['button'])
                pyautogui.keyUp(key)
                print("keyUp on {}".format(key))
            elif action['type'] == 'click':
                pyautogui.click(action['pos'][0],
                action['pos'][1], duration=0.25)

            try:
                next_action = data[index + 1]
            except IndexError:
                break 
            elapsed_time = next_action['time'] - action['time']      

            if elapsed_time < 0:
                raise Exception('Unexpected action ordering.')


            elapsed_time -= (time() - action_start_time)
            if elapsed_time < 0:
                elapsed_time = 0
            print('sleeping for {}'.format(elapsed_time))
            sleep(elapsed_time)


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
        'shift_l': 'shiftleft',
        'shift_r': 'shiftright',
        'num_lock': 'numlock',
        'print_screen': 'printscreen',
        'scroll_lock': 'scrolllock',
    }

    cleaned_key = button.replace('Key.', '')

    if cleaned_key in PYNPUT_SPECIAL_CASE_MAP:
        return PYNPUT_SPECIAL_CASE_MAP[cleaned_key]

    return cleaned_key

if __name__ == "__main__":
    main()