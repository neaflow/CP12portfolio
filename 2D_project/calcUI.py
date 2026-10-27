import tkinter as tk

import calc


def press(text):
    entry.insert(tk.END, text)


def clear():
    entry.delete(0, tk.END)
    result_var.set("")


def show_result():
    result_var.set(calc.calculate(entry.get()))


root = tk.Tk()
root.title("Calculator")

entry = tk.Entry(root)
entry.grid(row=0, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
entry.focus_set()
entry.bind("<Return>", lambda event: show_result())  # Enter also works

result_var = tk.StringVar()
tk.Label(root, textvariable=result_var, anchor="w", justify="left").grid(
    row=1, column=0, columnspan=4, sticky="ew", padx=5, pady=5)

buttons = [
    ["(", ")", "^", "C"],["7", "8", "9", "/"],["4", "5", "6", "*"],["1", "2", "3", "-"],["0", ".", "=", "+"],
]

for row_index, row in enumerate(buttons, start=2):
    for column_index, label in enumerate(row):
        if label == "C":
            command = clear
        elif label == "=":
            command = show_result
        else:
            command = lambda text=label: press(text)
        tk.Button(root, text=label, command=command).grid(
            row=row_index, column=column_index, sticky="nsew", padx=2, pady=2)

for column_index in range(4):
    root.columnconfigure(column_index, weight=1)

root.mainloop()
