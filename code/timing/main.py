import pyautogui
from time import time, sleep

# Tutorial - https://www.youtube.com/watch?v=RhVrxJIFws8
# argparse - https://docs.python.org/dev/library/argparse.html

DELAY_BETWEEN_COMMANDS = 1.00

def main():
    initializePyAutoGUI()
#    countdownTimer()
    reportMousePosition()

def initializePyAutoGUI():
    pyautogui.FAILSAFE = True

# def countdownTimer():
#    print("Starting", end="")
#    for i in range(0,5):
#        print(".", end="")
#        sleep(1)
#    print("Go")

# def holdKey(key, secs=1.00):
#    pyautogui.keyDown(key)
#    sleep(secs)
#    pyautogui.keyUp(key)
#    sleep(DELAY_BETWEEN_COMMANDS)

def reportMousePosition(secs=10):
    for i in range(0, secs):
        print(pyautogui.position())
        sleep(1)

if __name__ == "__main__":
    main()