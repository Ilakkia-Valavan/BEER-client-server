from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel

console = Console()

def render_board():
    # Example game board lines as string
    board_text = "\n".join([
        "Player 1:",
        "A B C",
        "1 . . .",
        "2 . . .",
        "3 . . .",
        "",
        "Player 2:",
        "A B C",
        "1 . . .",
        "2 . . .",
        "3 . . ."
    ])
    return Panel(board_text, title="Game Board", border_style="green")

def render_chat(chat_lines):
    chat_text = "\n".join(chat_lines)
    return Panel(chat_text, title="Chat", border_style="blue")

def main():
    chat_lines = [
        "[CHAT] Alice: Hello!",
        "[CHAT] Bob: Your turn.",
        "[CHAT] Alice: Nice hit!"
    ]

    layout = Layout()
    # Split terminal horizontally: left and right
    layout.split_row(
        Layout(render_board(), name="left"),
        Layout(render_chat(chat_lines), name="right")
    )

    console.print(layout)

if __name__ == "__main__":
    main()
