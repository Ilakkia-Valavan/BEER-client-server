from prompt_toolkit.application import Application
from prompt_toolkit.layout import Layout, HSplit
from prompt_toolkit.widgets import TextArea
from prompt_toolkit.key_binding import KeyBindings

chat_box = TextArea(text="Chat history...\n", height=10, read_only=True)
board_box = TextArea(text="Game board...\n", height=10, read_only=True)

def accept(buff):
    msg = input_field.text
    chat_box.text += f"\n> {msg}"
    input_field.buffer.document = input_field.buffer.document.empty

input_field = TextArea(height=1, prompt="> ", multiline=False, wrap_lines=True, accept_handler=accept)

layout = Layout(HSplit([board_box, chat_box, input_field]), focused_element=input_field)

kb = KeyBindings()
@kb.add("c-c")
def exit_(event):
    event.app.exit()

app = Application(layout=layout, key_bindings=kb, full_screen=True)
app.run()



"""
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
"""
