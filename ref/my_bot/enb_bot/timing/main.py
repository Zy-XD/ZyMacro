import pyautogui
from time import time, sleep

DELAY_BETWEEN_COMMANDS = 1.00

def main():
    initializePyAutoGui()
    countdownTimer()
    reportMousePosition()


def initializePyAutoGui():
    pyautogui.FAILSAFE = True

def countdownTimer():
    print("Starting", end="")
    for i in range(0, 5):
        print(".", end="")
        sleep(1)
    print("Go")    

def holdKey(key, seconds=1.00):
    pyautogui.keyDown(key)
    sleep(seconds)
    pyautogui.keyUp(key)
    sleep(DELAY_BETWEEN_COMMANDS)

def reportMousePosition(seconds=10):
    for i in range(0, seconds):
        print(pyautogui.position())
        sleep(1)


if __name__ == "__main__":
    main()