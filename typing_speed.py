"""A simple desktop typing-speed practice app built with Tkinter."""

import time
import tkinter as tk
from tkinter import ttk


PASSAGES = [
    "Small steps every day can lead to remarkable progress. Stay curious, keep practicing, and enjoy the process of learning something new.",
    "The best way to improve a skill is to use it often. Focus on steady progress, learn from mistakes, and celebrate each little win.",
    "A quiet morning is a lovely time to plan the day. Make a warm drink, open the window, and give your ideas room to grow.",
]

BG = "#10151d"
CARD = "#19212d"
TEXT = "#edf2f7"
MUTED = "#9ba9ba"
ACCENT = "#71e0b5"
FONT = "Segoe UI"


class TypingSpeedApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TypeFlow | Typing Speed")
        self.root.geometry("780x680")
        self.root.minsize(640, 580)
        self.root.configure(bg=BG)

        self.passage_index = 0
        self.started_at = None
        self.finished = False
        self.after_id = None
        self._style()
        self._build()
        self._set_passage()

    def _style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TCombobox", fieldbackground=CARD, background=CARD,
                        foreground=TEXT, arrowcolor=ACCENT, padding=7)
        style.map("TCombobox", fieldbackground=[("readonly", CARD)],
                  foreground=[("readonly", TEXT)])

    def _build(self):
        outer = tk.Frame(self.root, bg=BG, padx=34, pady=28)
        outer.pack(fill="both", expand=True)

        header = tk.Frame(outer, bg=BG)
        header.pack(fill="x", pady=(0, 22))
        tk.Label(header, text="TYPEFLOW", bg=BG, fg=ACCENT,
                 font=(FONT, 10, "bold")).pack(anchor="w")
        tk.Label(header, text="Find your typing rhythm", bg=BG, fg=TEXT,
                 font=(FONT, 25, "bold")).pack(anchor="w", pady=(4, 2))
        tk.Label(header, text="Type the passage below. Your timer starts with your first key.",
                 bg=BG, fg=MUTED, font=(FONT, 10)).pack(anchor="w")

        stats = tk.Frame(outer, bg=CARD, padx=20, pady=16)
        stats.pack(fill="x", pady=(0, 18))
        for i, (title, attr, value) in enumerate([
            ("WORDS / MIN", "wpm_var", "0"), ("ACCURACY", "accuracy_var", "—"),
            ("TIME", "time_var", "00:00"),
        ]):
            cell = tk.Frame(stats, bg=CARD)
            cell.grid(row=0, column=i, sticky="ew", padx=(0 if i == 0 else 20, 0))
            stats.grid_columnconfigure(i, weight=1)
            setattr(self, attr, tk.StringVar(value=value))
            tk.Label(cell, text=title, bg=CARD, fg=MUTED,
                     font=(FONT, 8, "bold")).pack(anchor="w")
            tk.Label(cell, textvariable=getattr(self, attr), bg=CARD, fg=TEXT,
                     font=(FONT, 23, "bold")).pack(anchor="w", pady=(3, 0))

        row = tk.Frame(outer, bg=BG)
        row.pack(fill="x", pady=(0, 8))
        tk.Label(row, text="SAMPLE TEXT", bg=BG, fg=MUTED,
                 font=(FONT, 9, "bold")).pack(side="left")
        self.passage_choice = tk.StringVar(value="Passage 1")
        self.selector = ttk.Combobox(row, textvariable=self.passage_choice,
                                     values=[f"Passage {i + 1}" for i in range(len(PASSAGES))],
                                     state="readonly", width=13)
        self.selector.pack(side="right")
        self.selector.bind("<<ComboboxSelected>>", self._choose_passage)

        self.passage_card = tk.Frame(outer, bg=CARD, padx=18, pady=16)
        self.passage_card.pack(fill="x", pady=(0, 16))
        self.passage_label = tk.Label(self.passage_card, text="", bg=CARD, fg=TEXT,
                                      justify="left", anchor="w", wraplength=660,
                                      font=(FONT, 12), padx=0, pady=2)
        self.passage_label.pack(fill="x")

        tk.Label(outer, text="YOUR TYPING", bg=BG, fg=MUTED,
                 font=(FONT, 9, "bold")).pack(anchor="w", pady=(0, 8))
        self.entry = tk.Text(outer, height=6, wrap="word", undo=True, padx=15, pady=13,
                             bg="#141c26", fg=TEXT, insertbackground=ACCENT,
                             selectbackground="#315b54", relief="flat",
                             font=(FONT, 12), highlightthickness=1,
                             highlightbackground="#293544", highlightcolor=ACCENT,
                             spacing1=3, spacing3=3)
        self.entry.pack(fill="both", expand=True)
        self.entry.bind("<KeyRelease>", self._on_typing)
        self.entry.bind("<<Paste>>", self._on_typing)

        footer = tk.Frame(outer, bg=BG)
        footer.pack(fill="x", pady=(16, 0))
        self.status_var = tk.StringVar(value="Ready when you are.")
        tk.Label(footer, textvariable=self.status_var, bg=BG, fg=MUTED,
                 font=(FONT, 9)).pack(side="left", fill="x", expand=True)
        self.finish_button = tk.Button(footer, text="Finish", command=self.finish,
                                       bg=ACCENT, fg="#10221d", activebackground="#91edca",
                                       activeforeground="#10221d", relief="flat", bd=0,
                                       padx=20, pady=9, font=(FONT, 9, "bold"), cursor="hand2")
        self.finish_button.pack(side="right", padx=(8, 0))
        self.reset_button = tk.Button(footer, text="Start over", command=self.reset,
                                      bg=CARD, fg=TEXT, activebackground="#273343",
                                      activeforeground=TEXT, relief="flat", bd=0,
                                      padx=16, pady=9, font=(FONT, 9), cursor="hand2")
        self.reset_button.pack(side="right")

    def _set_passage(self):
        self.target = PASSAGES[self.passage_index]
        self.passage_label.config(text=self.target)

    def _choose_passage(self, _event=None):
        self.passage_index = self.selector.current()
        self._set_passage()
        self.reset()

    def _on_typing(self, _event=None):
        if self.finished:
            return
        typed = self.entry.get("1.0", "end-1c")
        if typed and self.started_at is None:
            self.started_at = time.monotonic()
            self.status_var.set("Typing… keep going!")
            self._tick()
        self._update_stats(typed)
        if typed == self.target:
            self.finish()

    def _tick(self):
        if self.started_at is None or self.finished:
            return
        self._update_stats(self.entry.get("1.0", "end-1c"))
        self.after_id = self.root.after(250, self._tick)

    def _update_stats(self, typed):
        if not typed or self.started_at is None:
            self.wpm_var.set("0")
            self.accuracy_var.set("—")
            self.time_var.set("00:00")
            return
        elapsed = max(time.monotonic() - self.started_at, 0.01)
        minutes = elapsed / 60
        words = len(typed.split())
        self.wpm_var.set(str(round(words / minutes)))
        matched = sum(1 for i, char in enumerate(typed) if i < len(self.target) and char == self.target[i])
        accuracy = matched / max(len(typed), 1) * 100
        self.accuracy_var.set(f"{accuracy:.0f}%")
        seconds = int(elapsed)
        self.time_var.set(f"{seconds // 60:02d}:{seconds % 60:02d}")

    def finish(self):
        if self.finished:
            return
        if self.started_at is None:
            self.status_var.set("Type a little first, then finish your run.")
            return
        self._update_stats(self.entry.get("1.0", "end-1c"))
        self.finished = True
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.entry.config(state="disabled")
        self.selector.config(state="disabled")
        self.finish_button.config(state="disabled", bg="#40564f", fg="#c6d7d0")
        self.status_var.set("Passage complete!" if self.entry.get("1.0", "end-1c") == self.target
                            else "Run finished. Start over whenever you’re ready.")

    def reset(self):
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.started_at = None
        self.finished = False
        self.entry.config(state="normal")
        self.entry.delete("1.0", "end")
        self.selector.config(state="readonly")
        self.finish_button.config(state="normal", bg=ACCENT, fg="#10221d")
        self.wpm_var.set("0")
        self.accuracy_var.set("—")
        self.time_var.set("00:00")
        self.status_var.set("Ready when you are.")
        self.entry.focus_set()


def main():
    root = tk.Tk()
    TypingSpeedApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
