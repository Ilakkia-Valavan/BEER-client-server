import sys
import time
import msvcrt

def main():
    timeout = 20  # seconds
    print(f"Waiting for input for {timeout} seconds...")
    start_time = time.time()

    while True:
        if msvcrt.kbhit():
            char = sys.stdin.readline()
            print("You entered:", char.strip())
            break
        if time.time() - start_time > timeout:
            print("Timeout: no input received.")
            break
        time.sleep(0.1)

main()
