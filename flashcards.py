import json
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

class FlashcardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Flashcards, Inc")
        self.root.geometry("900x600")
        self.root.resizable(False, False)

        self.cards = []
        self.current_index = 0
        self.showing_front = True

        self.decks_dir = Path("Card Decks/Japanese")

        self.label = tk.Label(root, text="Select a deck:", font=("Yu Gothic", 14))
        self.label.pack(pady=80)

        self.json_files = []
        self.json_paths = {}
        if self.decks_dir.exists():
            for json_file in self.decks_dir.rglob("*.json"):
                name = json_file.stem
                display_name = name.replace("-", " ").replace("_", " ").title()
                self.json_files.append(display_name)
                self.json_paths[display_name] = json_file

        if not self.json_files:
            messagebox.showerror("Error", "No .json files found in Card Decks/Japanese or its subfolders")
            root.quit()
            return

        self.json_files.sort()

        self.selected_deck = tk.StringVar()
        self.deck_combo = ttk.Combobox(
            root,
            textvariable=self.selected_deck,
            values=self.json_files,
            state="readonly",
            font=("Yu Gothic", 12),
            width=40
        )
        self.deck_combo.pack(pady=20)
        self.deck_combo.current(0)

        self.load_btn = tk.Button(
            root,
            text="Load Deck",
            font=("Yu Gothic", 14),
            command=self.load_selected_deck,
            width=15,
            height=2
        )
        self.load_btn.pack(pady=40)

        self.root.bind("<Return>", lambda e: self.load_selected_deck())

        self.card_label = None

    def get_length_based_font_size(self, text, is_front=False):
        if not text.strip():
            return 60

        lines = text.split('\n')
        longest_line = max(lines, key=len)
        char_count = len(longest_line)

        print(f"Text: '{text}' | Longest line chars: {char_count} | is_front={is_front}")

        if is_front:
            if char_count <= 2:
                return 100
            if char_count <= 15:
                return 60
            elif char_count <= 30:
                return 50
            elif char_count <= 40:
                return 44
            else:
                return 30

        if char_count <= 15:
            return 52
        elif char_count <= 30:
            return 45
        elif char_count <= 40:
            return 38
        else:
            return 25

    def load_selected_deck(self):
        display_name = self.selected_deck.get()
        if not display_name:
            return

        json_path = self.json_paths.get(display_name)
        if not json_path or not json_path.exists():
            messagebox.showerror("Error", f"Could not find file for {display_name}")
            return

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                self.cards = json.load(f)
            if not self.cards:
                raise ValueError("Deck is empty")
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load {json_path.name}:\n{e}")
            return

        self.label.pack_forget()
        self.deck_combo.pack_forget()
        self.load_btn.pack_forget()

        self.show_flashcard_interface()

        self.current_index = 0
        self.showing_front = True
        self.update_card()
        self.update_buttons()

    def show_flashcard_interface(self):
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(
            main_frame,
            text=f"Deck: {self.selected_deck.get()}",
            font=("Yu Gothic", 12),
            bg="#f0f0f0"
        ).pack(anchor="n", pady=(10, 20))

        card_frame = tk.Frame(
            main_frame,
            bg="white",
            highlightbackground="#bbbbbb",
            highlightthickness=1,
            bd=0,
            relief="flat"
        )
        card_frame.pack(fill="both", expand=True, padx=40, pady=(20, 50))

        self.card_label = tk.Label(
            card_frame,
            text="",
            bg="white",
            fg="#000000",
            justify="center",
            anchor="center"
        )
        self.card_label.pack(expand=True, fill="both", padx=60, pady=40)

        self.card_label.bind("<Button-1>", lambda e: self.flip_card())

        button_bar = tk.Frame(main_frame, bg="#e8e8e8", height=110)
        button_bar.pack(side="bottom", fill="x", pady=(20, 10))
        button_bar.pack_propagate(False)

        btn_font = ("Yu Gothic", 16, "bold")

        tk.Button(
            button_bar, text="Previous", font=btn_font, width=12, height=2,
            command=self.prev_card
        ).pack(side="left", padx=40, expand=True)

        tk.Button(
            button_bar, text="Flip", font=btn_font, width=12, height=2,
            command=self.flip_card
        ).pack(side="left", padx=40, expand=True)

        tk.Button(
            button_bar, text="Next", font=btn_font, width=12, height=2,
            command=self.next_card
        ).pack(side="left", padx=40, expand=True)

    def update_card(self):
        if not self.cards:
            return
        
        card = self.cards[self.current_index]
        
        if self.showing_front:
            text = card.get("radical", "?").strip()   # ← changed to "radical" key
        else:
            romaji = card.get("romaji", "").strip()
            english = card.get("english", "").strip()
            parts = [p for p in [romaji, english] if p]
            text = "\n".join(parts) or "?"

        font_size = self.get_length_based_font_size(text, is_front=self.showing_front)

        self.card_label.config(
            text=text,
            font=("Yu Gothic", font_size, "bold"),
            wraplength=680
        )

    def flip_card(self):
        self.showing_front = not self.showing_front
        self.update_card()

    def next_card(self):
        if self.current_index < len(self.cards) - 1:
            self.current_index += 1
            self.showing_front = True
            self.update_card()
            self.update_buttons()

    def prev_card(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.showing_front = True
            self.update_card()
            self.update_buttons()

    def update_buttons(self):
        pass


if __name__ == "__main__":
    root = tk.Tk()
    app = FlashcardApp(root)
    root.mainloop()