from pathlib import Path
import random
import tkinter


# the files and settings that never change
words_file = Path(__file__).with_name("words.txt")
max_guesses = 6
word_length = 5

colors = {
    "correct": "#6aaa64",
    "present": "#c9b458",
    "absent": "#787c7e",
    "empty": "#ffffff",
    "border": "#d3d6da",
    "background": "#ffffff",
    "text": "#1a1a1b",
    "key": "#d3d6da",
}

all_words = []

#this is where the answer the player has to guess is kept
answer = ""
current_row = 0
current_guess = []
finished = 0

#goes into the window
root = None
tiles = []


def load_words():
    try:
        filetext = words_file.read_text(encoding="utf-8")#hold every word as a string
    except OSError as error:
        raise SystemExit("reading words broke at " + str(words_file) + ": " + str(error))

    words = []
    for line in filetext.splitlines():
        oneline = line.strip().lower()
        if len(oneline) == 5 and oneline.isalpha():
            if oneline not in words:
                words.append(oneline)#full wordlist

    if len(words) == 0:
        raise SystemExit("there are no words.")

    words.sort()
    return words


def score_guess(guess, answer):
    marks = ["absent"] * word_length
    still_left = list(answer)

    for index in range(len(guess)):
        if guess[index] == answer[index]:
            marks[index] = "correct"
            still_left[index] = None

    for index in range(len(guess)):
        if marks[index] != "correct" and guess[index] in still_left:
            marks[index] = "present"
            still_left[still_left.index(guess[index])] = None

    return marks


def build_the_game():
    global all_words, tiles

    all_words = load_words()

    root.title("AIdle")
    root.configure(bg=colors["background"])
    root.resizable(False, False)

    content = tkinter.Frame(root, bg=colors["background"])
    content.pack(padx=12, pady=4)
    game_area = tkinter.Frame(content, bg=colors["background"])
    game_area.pack(side="left", padx=(0, 18), anchor="n")

    #6*5 grid
    tiles = []
    board = tkinter.Frame(game_area, bg=colors["background"])
    board.pack(padx=12, pady=4)
    for row in range(max_guesses):
        tiles_in_row = []
        for column in range(word_length):
            onetile = tkinter.Label(
                board,
                text="",
                width=2,
                height=1,
                font=("Helvetica", 22, "bold"),
                bg=colors["background"],
                fg=colors["text"],
                relief="solid",
                bd=2,
                highlightthickness=0,
            )
            onetile.grid(row=row, column=column, padx=3, pady=3, ipadx=3, ipady=5)
            tiles_in_row.append(onetile)
        tiles.append(tiles_in_row)

    root.bind("<Key>", on_keypress)
    new_game()


def new_game():
    global answer, current_row, current_guess, finished

    answer = random.choice(all_words)
    current_row = 0
    current_guess = []
    finished = 0

    for row in range(len(tiles)):
        for column in range(len(tiles[row])):
            tiles[row][column].config(
                text="", bg=colors["background"], fg=colors["text"], bd=2
            )


def add_letter(letter):
    global current_guess
    if finished == 1 or len(current_guess) == word_length:
        return
    current_guess.append(letter)
    refresh_current_row()


def delete_letter():
    global current_guess
    if finished == 1 or len(current_guess) == 0:
        return
    current_guess.pop()
    refresh_current_row()


def refresh_current_row():
    for index in range(word_length):
        if index < len(current_guess):
            letter = current_guess[index].upper()
        else:
            letter = ""
        tiles[current_row][index].config(text=letter)


def submit_guess():
    global current_row, current_guess, finished

    if finished == 1:
        return
    if len(current_guess) != word_length:
        return

    guess = "".join(current_guess)
    if guess not in all_words:
        current_guess = []
        refresh_current_row()
        return

    states = score_guess(guess, answer)
    for index in range(len(guess)):
        state = states[index]
        tiles[current_row][index].config(bg=colors[state], fg="white", bd=0)

    if guess == answer:
        finished = 1
        return

    current_row = current_row + 1
    current_guess = []
    if current_row == max_guesses:
        finished = 1


def on_keypress(event):
    if event.keysym == "Return":
        submit_guess()
    elif event.keysym == "BackSpace":
        delete_letter()
    elif event.char.isalpha() and event.char.isascii():
        add_letter(event.char.lower())


def play():
    global root
    wordlist = load_words()
    if len(wordlist) == 0:
        return#stop if there's no words
    root = tkinter.Tk()
    build_the_game()
    root.mainloop()


if __name__ == "__main__":
    play()
