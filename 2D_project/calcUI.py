import tkinter as tk

import calc


def show_result():
    result_var.set(calc.calculate(entry.get()))


root = tk.Tk()
root.title("Calculator")
root.geometry("360x110")

entry = tk.Entry(root, font=("TkDefaultFont", 14))
entry.pack(fill="x", padx=10, pady=(10, 5))
entry.focus_set()
entry.bind("<Return>", lambda event: show_result())  # Enter also works

tk.Button(root, text="=", command=show_result).pack(fill="x", padx=10)

result_var = tk.StringVar()
tk.Label(root, textvariable=result_var, anchor="w", justify="left",
         wraplength=340).pack(fill="x", padx=10, pady=10)

root.mainloop()
