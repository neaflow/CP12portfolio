#NOTE: a lot of this code was *borrowed* from OpenAI and openrouter docs. shoutout them. the rest was written by me running on fumes in a 13-hours straight session
#i had to make sure that these were all installed on the school comptuers without needing to pip install anything
from pathlib import Path#finding words.txt
import json#openrouter api sends json
import queue#need this for streaming token by token
import random#randomly choose the answer word
import re#finding GUESS: xxxxx in the LLM response and setting it as the guess
import threading#makes the LLM stuff run seperately from the widnow so the windoew doens't freeze while the llm works
import tkinter#making the winow
from urllib.error import HTTPError, URLError#errors
from urllib.request import Request, urlopen#making requests on the internet

# the files and settings that never change
words_file = Path(__file__).with_name("words.txt")
api_url = "https://openrouter.ai/api/v1/chat/completions"
max_guesses = 6
word_length = 5

#kept having to adjust these nex variables until it'd stop being stupid
#update: this is mostly old legacy stuff from the old LLM options that were completely broken and braindead. this was to try to help them. they're hopeless.
max_reply_tokens = 1200
max_think_tokens = 150
thinking_off = 0
max_retries = 3
max_restarts = 3

#the only model this game uses. the other ones are just not good enough. i can't figure out how to fix them. i've tried for hours. if you think you can fix it, godspeed.
model_id = "openai/gpt-6-luna"

system_prompt = """You're playing Wordle. The answer is a common five-letter English word. You have six guesses.
ON YOUR FIRST TURN there is no feedback yet, because you have not guessed anything. Just pick a strong opening word and go. Do not ask me for feedback, do not ask what the rules are, do not ask for the board. I will always send you feedback after every guess, so on later turns the feedback for your last guess is at the bottom of my message.
Answer format, follow it exactly every time:
- Line 1: your reasoning, 2-3 short sentences. No more.
- Line 2: your guess, exactly like this: GUESS: xxxxx
- Then stop. Write nothing after the GUESS line.
Keep the whole reply under 60 words. No headers, no bullet lists, no lists of alternatives, no follow-up suggestions.
How to read my feedback. I describe every letter in a full sentence:
- "X is correct and in the Nth spot" means X is locked in that exact position. Keep it there.
- "X is in the word but NOT in the Nth spot" means X is in the word SOMEWHERE ELSE, and definitely not there. This is the one people get wrong. It never means X belongs in that spot.
- "X is not in the word at all" means X is not in the word.
Two rules that will lose you the game if you ignore them:
1. NEVER play a guess where every letter is already known to you. If your word contains no letter you have never seen feedback for, you learn nothing and you have wasted a turn. Every guess you make, apart from your very last one, must contain at least one letter you have not yet had feedback on.
2. NEVER repeat a guess you already made. The list of words you have already guessed is sent with every feedback message, and all of them are banned.
How to choose each guess:
- Opening turn: play a word packed with the most common letters, so you get feedback on as much of the alphabet as possible. Hint: CRANE and SLATE are both good.
- If you already know the pattern but not every letter, use a word that fits that pattern and also carries one or two letters you have never had feedback on. That is how you test them cheaply.
- If exactly two or three candidate words still fit, and you have guesses to spare, you may test the one you think is least likely, but only if it also tells you something new.
- Your LAST guess: you must commit to one word. Do not play a probe word with no guesses left, because then you cannot correct yourself.
If a letter is known to be in the word but not in the spot you tried, you must place it in a different spot. Working out where is the whole game.
Use a real five-letter word from the English word list, not an invented one.
If you have 2 or more guesses left and you know four of the letters to be in the correct place, you should avoid writing the same word with the one unknown letter changed, as if you
end up being incorrect, you wasted an entire guess to learn one new letter. You should try to maximize clues in this case. make sure to use all clues on your last guess."""

closing_win_prompt = """System: The game is over: you WON! Your last guess was correct.
You do not need to make another guess. Do NOT include a GUESS: line."""

closing_loss_prompt = """System: The game is over: you LOST. You have used all six guesses
without finding the answer. You do not need to make another guess. Do NOT include a GUESS: line."""

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
key_states = {}

# the words the llm already used (it is not allowed to use them again)
llm_guesses = []
llm_messages = []
llm_active = 0
llm_waiting = 0
llm_closing = 0
streaming_reasoning_shown = 0

# how many times in a row we have asked again because no guess was in the reply (this was for debugging)
llm_retries = 0
# how many times we have thrown the messages away and started the turn over
llm_restarts = 0

#or else an old game's answers would keep being played in a new game
game_id = 0

#goes into the window
root = None
message_label = None
message_timer = None
tiles = []
key_buttons = {}
llm_output = None
llm_button = None

responses = None
stream_tokens = None
api_key = ""

# the thread that is currently talking to openrouter, so the stop button can
# shut the connection down. it is None when nothing is running
current_cancel = None
active_response = None


def load_words():
    try:
        filetext = words_file.read_text(encoding="utf-8")
    except OSError as error:
        raise SystemExit("Could not load word list at " + str(words_file) + ": " + str(error))

    words = []
    for line in filetext.splitlines():
        oneline = line.strip().lower()
        if len(oneline) == 5 and oneline.isalpha():
            if oneline not in words:
                words.append(oneline)

    if len(words) == 0:
        raise SystemExit("No five-letter words found in " + str(words_file))

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

#Without the next two functions, the LLM was absolutely terrible at guessing. I don't know why this fixes it.
def position_word(index):
    names = ["first", "second", "third", "fourth", "fifth"]
    return names[index]

# turn the tile colours into sentences
def describe_guess(guess, states):

    parts = []
    for index in range(len(guess)):
        letter = guess[index].upper()
        where = position_word(index)
        if states[index] == "correct":
            parts.append(letter + " is correct and in the " + where + " spot")
        elif states[index] == "present":
            parts.append(letter + " is in the word but NOT in the " + where + " spot")
        else:
            parts.append(letter + " is not in the word at all")

    return "For your guess " + guess.upper() + ": " + ". ".join(parts) + "."


def check_guess(guess):
    # see if the model broke a rule it should already know about, like playing
    # a letter that was ruled out. the weak models do this a lot, so we catch
    # it and tell them why instead of wasting a turn on it
    if guess in llm_guesses:
        return ""

    banned = set()
    locked = {}
    misplaced = {}

    for played in llm_guesses:
        states = score_guess(played, answer)
        for index in range(word_length):
            letter = played[index]
            if states[index] == "absent":
                if letter not in locked and letter not in misplaced:
                    banned.add(letter)
            elif states[index] == "correct":
                if letter not in locked:
                    locked[letter] = set()
                locked[letter].add(index)
            else:
                if letter not in locked:
                    misplaced.setdefault(letter, set()).add(index)

    # Check if we're on the last guess (5 guesses used already, this would be the 6th)
    is_final_guess = len(llm_guesses) == (max_guesses - 1)

    for index in range(word_length):
        letter = guess[index]
        # Block if a letter was tried in this exact position and came back "present" (wrong spot)
        if letter in misplaced and index in misplaced[letter]:
            return letter.upper() + " was already tried in the " + position_word(index) + " spot and came back wrong, so it cannot be there again."

    # On the final guess, validate that all confirmed letters are in correct positions
    if is_final_guess:
        for letter, positions in locked.items():
            for pos in positions:
                if guess[pos] != letter:
                    return letter.upper() + " must be in the " + position_word(pos) + " spot."

    return ""


def describe_board():
    # rebuild the whole board from the guesses we already have, so we can show
    # it back to the model when it has lost the thread
    letters = {"correct": "G", "present": "Y", "absent": "X"}
    lines = []
    for guess in llm_guesses:
        states = score_guess(guess, answer)
        marks = "".join(letters[states[index]] for index in range(word_length))
        lines.append("- you played " + guess.upper() + " and got " + marks)
    if lines == []:
        lines.append("- you have not played anything yet")

    left = max_guesses - len(llm_guesses)
    return (
        "Here is the board so far, all of it in one place:\n"
        + "\n".join(lines) + "\n"
        + "For each letter in that word, G means it is correct and in that spot, "
        + "Y means the letter is in the word but NOT in that spot, "
        + "and X means the letter is not in the word at all.\n"
        + "You have played " + str(len(llm_guesses)) + " words. You have " + str(left) + " guesses left.\n"
        + "Words you have already played, all banned: " + ", ".join(llm_guesses) + ".\n"
    )


def add_key(parent, label, command, wide=False):
    # one button on the keyboard. wide=True makes it bigger (for ENTER and DEL)
    button = tkinter.Button(
        parent,
        text=label,
        command=command,
        width=5 if wide else 3,
        height=2,
        font=("Helvetica", 9, "bold"),
        relief="flat",
        bg=colors["key"],
        fg=colors["text"],
        activebackground="#bfc3c6",
    )
    button.pack(side="left", padx=2)
    if len(label) == 1 and label.isalpha():
        key_buttons[label.lower()] = button

#lot of visual stuff
def build_the_game():
    global all_words, responses, stream_tokens
    global message_label, tiles, key_buttons, llm_output, llm_button, stop_button

    all_words = load_words()

    root.title("AIdle")
    root.configure(bg=colors["background"])
    root.resizable(False, False)

    responses = queue.Queue()
    stream_tokens = queue.Queue()

    # the top bar with the name of the game and the new game button
    header = tkinter.Frame(root, bg=colors["background"])
    header.pack(fill="x", padx=16, pady=(10, 5))
    tkinter.Label(
        header,
        text="AIdle",
        font=("Helvetica", 24, "bold"),
        bg=colors["background"],
        fg=colors["text"],
    ).pack(side="left")
    
    # the stop button sits left of new game, so it reads left to right
    stop_button = tkinter.Button(
        header,
        text="Stop",
        command=stop_llm,
        font=("Helvetica", 10, "bold"),
        relief="flat",
        bg=colors["key"],
        padx=10,
        pady=5,
        state="disabled",
    )
    stop_button.pack(side="right", padx=(0, 6))

    tkinter.Button(
        header,
        text="New Game",
        command=new_game,
        font=("Helvetica", 10, "bold"),
        relief="flat",
        bg=colors["key"],
        padx=10,
        pady=5,
    ).pack(side="right")

    #message text for the user not the llm
    message_label = tkinter.Label(
        root,
        text="",
        font=("Helvetica", 11),
        bg=colors["background"],
        fg=colors["text"],
        height=2,
    )
    message_label.pack()

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

    #this isn't necessary but it's the on screen board from the acutal game
    keyboard = tkinter.Frame(game_area, bg=colors["background"])
    keyboard.pack(padx=5, pady=(12, 16))
    key_buttons = {}
    rows = ("QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM")
    for row_index in range(len(rows)):
        letters = rows[row_index]
        row_frame = tkinter.Frame(keyboard, bg=colors["background"])
        row_frame.pack(pady=3)
        if row_index == 2:
            add_key(row_frame, "ENTER", submit_guess, wide=True)
        for letter in letters:
            add_key(row_frame, letter, lambda key=letter: add_letter(key))
        if row_index == 2:
            #on linux the backspace logo doesn't work so "DEL" instead
            add_key(row_frame, "DEL", delete_letter, wide=True)

    # the gray panel on the right with everything the model says
    llm_panel = tkinter.Frame(content, bg="#f4f4f4", width=390, height=480)
    llm_panel.pack(side="left", fill="both", expand=True, anchor="n")
    llm_panel.pack_propagate(False)
    tkinter.Label(
        llm_panel,
        text="LLM PLAYER",
        font=("Helvetica", 14, "bold"),
        bg="#f4f4f4",
        fg=colors["text"],
    ).pack(anchor="w", padx=12, pady=(12, 4))
    llm_output = tkinter.Text(
        llm_panel,
        wrap="word",
        state="disabled",
        font=("Helvetica", 10),
        bg="white",
        fg=colors["text"],
        relief="solid",
        bd=1,
        padx=8,
        pady=8,
    )
    llm_output.pack(fill="both", expand=True, padx=10, pady=6)

    button_row = tkinter.Frame(llm_panel, bg="#f4f4f4")
    button_row.pack(fill="x", padx=10, pady=(2, 10))

    llm_button = tkinter.Button(
        button_row,
        text="Start LLM game",
        command=start_llm,
        font=("Helvetica", 10, "bold"),
        relief="flat",
        bg=colors["key"],
        padx=10,
        pady=7,
    )
    llm_button.pack(side="right")

    root.bind("<Key>", on_keypress)
    new_game()
    root.after(100, check_llm_responses)
    #immediately ask for api key for OR
    root.after(200, prompt_for_key)


def new_game():
    global game_id, answer, current_row, current_guess, finished, key_states
    global llm_guesses, llm_messages
    global llm_active, llm_waiting, llm_closing, streaming_reasoning_shown
    global current_cancel, llm_retries, llm_restarts

    game_id = game_id + 1
    # a new game invalidates any response still in flight
    if current_cancel is not None:
        current_cancel.set()
    current_cancel = None
    answer = random.choice(all_words)
    current_row = 0
    current_guess = []
    finished = 0
    key_states = {}
    llm_active = 0
    llm_waiting = 0
    llm_closing = 0
    streaming_reasoning_shown = 0
    llm_retries = 0
    llm_restarts = 0
    llm_guesses = []
    llm_messages = []
    llm_button.config(text="Start LLM game", state="normal")
    stop_button.config(state="disabled")
    set_llm_output(
        "Model: " + model_id + "\nPress start LLM game to let the model play this match\n"
    )
    clear_message()

    for row in range(len(tiles)):
        for column in range(len(tiles[row])):
            tiles[row][column].config(
                text="", bg=colors["background"], fg=colors["text"], bd=2
            )
    # and put all the keys back to gray
    for letter in key_buttons:
        key_buttons[letter].config(bg=colors["key"], fg=colors["text"])


def stop_llm():
    # kills the response that is coming in right now. it does not start a new
    # game, it just leaves the model wherever it happens to be
    global llm_waiting, llm_active, llm_closing, current_cancel

    if llm_waiting == 0:
        return

    llm_waiting = 0
    llm_closing = 0

    if current_cancel is not None:
        current_cancel.set()
    current_cancel = None

    # close the socket so the blocked read in the background thread wakes up
    # and stops instead of sitting there holding the connection open
    if active_response is not None:
        try:
            active_response.close()
        except (OSError, ValueError):
            pass

    # throw away the leftovers the thread already queued, otherwise the
    # half written answer would still land in the box
    drain_queues()

    if llm_active == 1:
        append_llm_output("\n(stopped)\n")
        llm_active = 0

    llm_button.config(text="Start LLM game", state="normal")
    stop_button.config(state="disabled")


def drain_queues():
    # empty both queues so nothing old shows up after we stop
    while True:
        try:
            stream_tokens.get_nowait()
        except queue.Empty:
            break
    while True:
        try:
            responses.get_nowait()
        except queue.Empty:
            break


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
    global current_row, current_guess, finished, key_states, llm_messages

    if finished == 1:
        return
    if len(current_guess) != word_length:
        show_message("not enough letters")
        return

    guess = "".join(current_guess).lower()
    if guess not in all_words:
        show_message("not in word list")
        #
        if llm_active == 1:
            append_llm_output("\nInvalid guess: " + guess.upper() + " (not in word list)\n")
            llm_messages.append({
                "role": "user",
                "content": "the guess " + guess + " is not in the valid word list. it did not use a turn. choose a valid five-letter word.",
            })
            current_guess = []
            refresh_current_row()
            request_llm_guess()
        return

    states = score_guess(guess, answer)
    # a key only ever gets a better color, it never goes back to gray
    priority = {"absent": 0, "present": 1, "correct": 2}
    for index in range(len(guess)):
        letter = guess[index]
        state = states[index]
        tiles[current_row][index].config(bg=colors[state], fg="white", bd=0)
        before = key_states.get(letter)
        if before is None or priority[state] > priority[before]:
            key_states[letter] = state
            key_buttons[letter].config(bg=colors[state], fg="white")

    if guess == answer:
        finished = 1
        show_message("You got it!", colors["correct"])
        if llm_active == 1:
            finish_llm("Solved in " + str(current_row + 1) + " guesses.")
        return

    current_row = current_row + 1
    current_guess = []
    if current_row == max_guesses:
        finished = 1
        show_message("The word was " + answer.upper())
        if llm_active == 1:
            finish_llm("Out of guesses. The word was " + answer.upper() + ".")
    else:
        #ask again
        if llm_active == 1:
            feedback = describe_guess(guess, states)
            llm_messages.append({
                "role": "user",
                "content": (
                    feedback + " "
                    + str(max_guesses - current_row) + " guesses remain. "
                    "Words already guessed (banned, do not repeat): " + ", ".join(llm_guesses) + ". "
                    "Make your next guess."
                ),
            })
            request_llm_guess()


def ask_for_api_key():
    #makes it open another smaller window popup
    dialog = tkinter.Toplevel(root)
    dialog.title("API key")
    dialog.configure(bg=colors["background"])
    dialog.resizable(False, False)
    dialog.transient(root)
    dialog.grab_set()

    frame = tkinter.Frame(dialog, bg=colors["background"], padx=16, pady=14)
    frame.pack()
    tkinter.Label(
        frame,
        text="Enter OpenRouter API key:",
        font=("Helvetica", 10, "bold"),
        bg=colors["background"],
        fg=colors["text"],
    ).pack(anchor="w")
    entry = tkinter.Entry(frame, show="*", width=48, font=("Helvetica", 11))#not showing what is typed is apperently good practice for api stuff
    entry.pack(anchor="w", pady=(8, 2))
    entry.focus_set()
    status_label = tkinter.Label(
        frame,
        text="",
        font=("Helvetica", 9),
        bg=colors["background"],
        fg="#c0392b",
        wraplength=320,
        justify="left",
    )
    status_label.pack(anchor="w")
    # a box instead of a normal variable, otherwise confirm() could not change it
    result = {"ok": False}
    buttons = tkinter.Frame(frame, bg=colors["background"])

    def set_buttons_enabled(enabled):
        # grey the buttons out while we are waiting for the key test
        for child in buttons.winfo_children():
            if enabled:
                child.config(state="normal")
            else:
                child.config(state="disabled")

    def confirm(event=None):
        # the unlock button was pressed
        # global here so the key we get stays saved after the popup is gone
        global api_key
        value = entry.get().strip()
        if value == "":
            status_label.config(text="Please enter an API key.")
            return
        status_label.config(text="Testing key...", fg=colors["text"])
        set_buttons_enabled(False)
        dialog.update_idletasks()

        ok, message = test_api_key(value)
        if not ok:
            status_label.config(text=message, fg="#c0392b")
            set_buttons_enabled(True)
            entry.focus_set()
            return
        api_key = value
        result["ok"] = True
        dialog.destroy()

    def cancel(event=None):
        # the cancel button was pressed
        dialog.destroy()

    tkinter.Button(buttons, text="Cancel", command=cancel, relief="flat",
                  bg=colors["key"], padx=10, pady=4).pack(side="left", padx=(0, 6))
    tkinter.Button(buttons, text="Unlock", command=confirm, relief="flat",
                  bg=colors["key"], padx=10, pady=4).pack(side="left")
    buttons.pack(anchor="e", pady=(10, 0))
    dialog.bind("<Return>", confirm)
    dialog.bind("<Escape>", cancel)

    dialog.wait_window()
    return result["ok"]

#FROM DOCS
def test_api_key(candidate_key):
    body = json.dumps({
        "model": model_id,
        "messages": [{"role": "user", "content": "Hi"}],
        "max_tokens": 1,
    }).encode("utf-8")
    request = Request(
        api_url,
        data=body,
        headers={
            "Authorization": "Bearer " + candidate_key,
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",
            "X-Title": "AIdle",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=30) as response:
            json.loads(response.read().decode("utf-8"))
        return True, ""
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        if error.code == 401 or error.code == 403:
            return False, "Key rejected: that key is not valid."
        if error.code == 429:
            return True, ""
        return False, "Key test failed (HTTP " + str(error.code) + "): " + detail[:120]
    except (URLError, TimeoutError) as error:
        return False, "Network error while testing key: " + str(error)


def prompt_for_key():
    #ask for the key when the game opens
    if api_key == "":
        ask_for_api_key()

#the start llm game button was pressed
def start_llm():

    global llm_active, llm_messages, llm_guesses, streaming_reasoning_shown, llm_retries, llm_restarts

    if api_key == "":
        if ask_for_api_key() == False:
            append_llm_output("API key not entered. LLM play cancelled.\n")
            return
    if finished == 1 or len(llm_guesses) > 0 or current_row > 0:
        new_game()

    llm_active = 1
    llm_button.config(text="LLM playing...", state="disabled")
    llm_messages = [{"role": "system", "content": system_prompt}]
    llm_guesses = []
    streaming_reasoning_shown = 0
    llm_retries = 0
    llm_restarts = 0
    set_llm_output("Model: " + model_id + "\n\n")
    request_llm_guess()


def request_llm_guess():

    global llm_waiting, current_cancel

    if llm_active == 0 or llm_waiting == 1:
        return
    llm_waiting = 1
    which_game = game_id
    messages = list(llm_messages)
    # fresh event for this request. the stop button sets it, the thread checks it
    current_cancel = threading.Event()
    if llm_closing == 1:
        label = "thinking about closing thoughts...\n"
    else:
        label = "Thinking...\n"
    append_llm_output("\n" + label)
    stop_button.config(state="normal")
    # this runs in the background so the window doesn't freeze while we wait
    threading.Thread(
        target=call_openrouter,
        args=(which_game, messages, current_cancel),
        daemon=True,
    ).start()

#FROM DOCS
def call_openrouter(which_game, messages, cancel):

    global active_response

    # effort none switches the thinking off completely. max_tokens is the
    # other option and just puts a limit on it, but none means no thinking at
    # all. the api only lets us send one of the two
    if thinking_off == 1:
        thinking = {"effort": "none"}
    else:
        thinking = {"max_tokens": max_think_tokens}

    body = json.dumps({
        "model": model_id,
        "messages": messages,
        "reasoning": thinking,
        "max_tokens": max_reply_tokens,
        "stream": True,
    }).encode("utf-8")
    request = Request(
        api_url,
        data=body,
        headers={
            "Authorization": "Bearer " + api_key,
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
            "HTTP-Referer": "http://localhost",
            "X-Title": "AIdle",
        },
        method="POST",
    )

    content_parts = []
    reasoning_parts = []

    def read_stream(response):
        # openrouter sends the answer back in small pieces, one line at a time.
        # the lines that start with "data:" are the ones with real words in them
        for line in response:
            # the user pressed stop, so quit the loop and let go of the socket
            if cancel.is_set():
                return
            line = line.decode("utf-8", errors="replace").strip()
            if not line.startswith("data:"):
                continue
            payload = line[len("data:"):].strip()
            if payload == "" or payload == "[DONE]":
                continue
            try:
                chunk = json.loads(payload)
            except ValueError:
                continue
            delta = chunk.get("choices", [{}])[0].get("delta") or {}
            token = delta.get("reasoning")
            if token:
                # the thinking part, we show it in gray under "Reasoning:"
                reasoning_parts.append(token)
                stream_tokens.put((which_game, "reasoning", token))
            token = delta.get("content")
            if token:
                # the actual answer
                content_parts.append(token)
                stream_tokens.put((which_game, "content", token))

    try:
        with urlopen(request) as response:
            active_response = response
            # no timeout here on purpose. openrouter can be slow to start a
            # stream and we would rather wait for the answer than kill the game
            read_stream(response)
        active_response = None
        if cancel.is_set():
            # stopped on purpose, so we do not report anything
            return
        content = "".join(content_parts)
        reasoning = "".join(reasoning_parts)
        responses.put((which_game, content, reasoning, None))
    except (HTTPError, URLError, TimeoutError, KeyError, IndexError, ValueError, OSError) as error:
        active_response = None
        if cancel.is_set():
            return
        if isinstance(error, HTTPError):
            detail = error.read().decode("utf-8", errors="replace")
        else:
            detail = str(error)
        responses.put((which_game, "", "", detail))


def check_llm_responses():
    # this runs again and again on the tkinter side. it takes everything the
    # background thread left in the queues and puts it into the window
    global llm_waiting, llm_active, llm_closing, streaming_reasoning_shown
    global llm_messages, llm_guesses, current_guess, current_cancel, llm_restarts, llm_retries

    try:
        # 1. show the words as they come in, before the answer is finished
        while True:
            try:
                which_game, kind, token = stream_tokens.get_nowait()
            except queue.Empty:
                break
            # throw away the words if they belong to a game we already closed
            if which_game != game_id:
                continue
            if kind == "reasoning" and streaming_reasoning_shown == 0:
                append_llm_output("\nreasoning:\n")
                streaming_reasoning_shown = 1
            append_llm_output(token)

        # 2. now the answer is done, so we can look for the guess in it
        while True:
            try:
                which_game, content, reasoning, error = responses.get_nowait()
            except queue.Empty:
                break
            if which_game != game_id:
                continue
            llm_waiting = 0
            current_cancel = None
            stop_button.config(state="disabled")
            if error:
                append_llm_output("\napi error: " + error + "\n")
                llm_active = 0
                llm_button.config(text="Start LLM game", state="normal")
                continue

            # the words were already shown while they were coming in, so here we
            # only have to close the block off
            if content.strip() == "":
                # some models only send back their thinking and no real answer
                if reasoning.strip() != "":
                    if streaming_reasoning_shown == 0:
                        append_llm_output("\nReasoning:\n" + reasoning.strip())
                    append_llm_output("\n(no content returned)")
                else:
                    append_llm_output("\n(empty response)")
            append_llm_output("\n")
            streaming_reasoning_shown = 0

            if llm_closing == 1:
                # the game is over and the model had its last say, so we stop
                llm_closing = 0
                llm_active = 0
                llm_button.config(text="Start LLM game", state="normal")
                continue

            llm_messages.append({"role": "assistant", "content": content})
            # some models write the guess into the thinking part instead of the
            # real reply, so we look in both. content first, then reasoning
            found = re.search(r"\bGUESS\s*:\s*([a-zA-Z]{5})\b", content, re.IGNORECASE)
            if not found:
                found = re.search(r"\bGUESS\s*:\s*([a-zA-Z]{5})\b", reasoning, re.IGNORECASE)
            if not found:
                # it ran out of words before it got to the guess, so we say
                # it again but only a few times before we start over
                llm_retries = llm_retries + 1
                if llm_retries > max_retries:
                    # it keeps messing up, so we wipe its messages and just
                    # hand it the board again, telling it to commit
                    llm_restarts = llm_restarts + 1
                    if llm_restarts > max_restarts:
                        append_llm_output("\nGave up asking for a usable guess.\n")
                        llm_active = 0
                        llm_button.config(text="Start LLM game", state="normal")
                        continue
                    append_llm_output("\nStarting this turn over with a clean board.\n")
                    llm_messages = [{"role": "system", "content": system_prompt}]
                    llm_messages.append({
                        "role": "user",
                        "content": (
                            describe_board()
                            + "You have already had your chance this turn and did not give me a usable guess, "
                            + "so make sure your reply is two lines and nothing else.\n"
                            + "You must give me a guess now. Do not ask me for anything.\n"
                            + "Line 1: one short sentence of reasoning. Line 2: GUESS: xxxxx"
                        ),
                    })
                    llm_retries = 0
                    request_llm_guess()
                    continue
                llm_messages.append({
                    "role": "user",
                    "content": "I could not find a guess in your reply, so you have wasted a turn. Reply with exactly two lines and nothing else. First line: one short sentence of reasoning. Second line: your word, written exactly like this and nothing after it: GUESS: xxxxx",
                })
                request_llm_guess()
                continue
            llm_retries = 0

            guess = found.group(1).lower()
            if guess in llm_guesses:
                append_llm_output(
                    "Repeated guess: " + guess.upper() + " was already used. Asking again.\n"
                )
                llm_messages.append({
                    "role": "user",
                    "content": (
                        "GUESS: " + guess + " is a repeat of one of your earlier guesses. It did not use a turn. "
                        "Banned words: " + ", ".join(llm_guesses) + ". Choose a different five-letter word. "
                        "Remember: a letter marked as in the word but not in that spot means the letter is "
                        "somewhere else in the word, not that it belongs in that spot. "
                        "Answer in under 60 words: 2-3 short sentences, then the GUESS line, then stop."
                    ),
                })
                request_llm_guess()
                continue
            if guess not in all_words:
                append_llm_output(
                    "Invalid guess: " + guess.upper() + " is not in the word list. Asking again.\n"
                )
                llm_messages.append({
                    "role": "user",
                    "content": "GUESS: " + guess + " is not in the valid word list. It did not use a turn. Choose a valid five-letter word. Answer in under 60 words: 2-3 short sentences, then the GUESS line, then stop.",
                })
                request_llm_guess()
                continue

            problem = check_guess(guess)
            if problem != "":
                # it broke a rule it should have known, so it did not use a
                # turn. we say exactly what it did wrong and ask again
                append_llm_output("Illegal guess: " + guess.upper() + ". " + problem + " Asking again.\n")
                llm_messages.append({
                    "role": "user",
                    "content": (
                        "That guess breaks a rule, so it did not use a turn. " + problem + " "
                        + "Check the board above and pick a different word. "
                        + "Answer in under 60 words: 2-3 short sentences, then the GUESS line, then stop."
                    ),
                })
                request_llm_guess()
                continue

            # it is a real word we have not used yet, so it goes on the board
            llm_guesses.append(guess)
            current_guess = list(guess)
            refresh_current_row()
            submit_guess()
    finally:
        root.after(100, check_llm_responses)


def set_llm_output(text):
    # wipe the llm box and put new text in it
    llm_output.config(state="normal")
    llm_output.delete("1.0", "end")
    llm_output.insert("end", text)
    llm_output.see("end")
    llm_output.config(state="disabled")


def append_llm_output(text):
    # add more text to the bottom of the llm box
    llm_output.config(state="normal")
    llm_output.insert("end", text)
    llm_output.see("end")
    llm_output.config(state="disabled")


def finish_llm(message):
    # the game is over, so we let the model say one last thing about it
    global llm_closing

    append_llm_output("\n" + message + "\n")
    # llm_active stays 1 on purpose, otherwise the closing request would not go
    # through. the button stays disabled until the last answer shows up
    llm_button.config(text="LLM wrapping up...", state="disabled")

    if "Solved" in message:
        won = True
    else:
        won = False
    if won == True:
        llm_messages.append({"role": "user", "content": closing_win_prompt})
    else:
        llm_messages.append({"role": "user", "content": closing_loss_prompt})
    llm_closing = 1
    request_llm_guess()


def show_message(text, color=colors["text"]):
    # the line of text above the board. it only shows for a couple of seconds and
    # then goes blank again, so it never sits there with old text in it
    global message_timer

    if message_timer is not None:
        root.after_cancel(message_timer)
    message_label.config(text=text, fg=color)
    message_timer = root.after(2000, clear_message)


def clear_message():
    # wipe the line of text above the board once the message has had its time
    global message_timer

    message_timer = None
    message_label.config(text="")


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
        return
    root = tkinter.Tk()
    build_the_game()
    root.mainloop()


if __name__ == "__main__":
    play()
