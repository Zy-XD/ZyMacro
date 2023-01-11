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

def reportMousePosition(secs=10):
    for i in range(0, secs):
        print(pyautogui.position())
        sleep(1)

if __name__ == "__main__":
    main()