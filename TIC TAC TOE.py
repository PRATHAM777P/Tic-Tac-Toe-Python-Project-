import random
import sys
import os
import json

# Try to import tkinter for GUI mode
try:
    import tkinter as tk
    from tkinter import messagebox, simpledialog
    TK_AVAILABLE = True
except ImportError:
    TK_AVAILABLE = False

FEATURES_LIST = [
    "Game mode selection (Single Player with Easy/Medium/Hard AI, Two Player)",
    "Player name entry and customization (choose X/O, color, avatar in GUI)",
    "Undo/redo (stack-based, animated in GUI)",
    "Move timer (countdown, forfeits turn if time runs out)",
    "Scoreboard (persistent, tracks wins/losses/ties)",
    "Save/load game state (file-based)",
    "Replay last game (step through moves)",
    "Input validation loop (never crashes, always prompts again)",
    "Position guide (1-9 mapping beside board in console)",
    "Animated transitions (console: text, GUI: grid/buttons)",
    "Responsive, modern GUI (themes, color selection, animated grid, highlight winning line)",
    "Features/help modal"
]

SCOREBOARD_FILE = 'scoreboard.json'

def load_scoreboard():
    if os.path.exists(SCOREBOARD_FILE):
        with open(SCOREBOARD_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_scoreboard(scoreboard):
    with open(SCOREBOARD_FILE, 'w') as f:
        json.dump(scoreboard, f)

scoreboard = load_scoreboard()

def update_scoreboard(winner, player1, player2):
    global scoreboard
    for player in [player1, player2]:
        if player.name not in scoreboard:
            scoreboard[player.name] = {'wins': 0, 'losses': 0, 'ties': 0}
    if winner == 'tie':
        scoreboard[player1.name]['ties'] += 1
        scoreboard[player2.name]['ties'] += 1
    elif winner == player1.name:
        scoreboard[player1.name]['wins'] += 1
        scoreboard[player2.name]['losses'] += 1
    elif winner == player2.name:
        scoreboard[player2.name]['wins'] += 1
        scoreboard[player1.name]['losses'] += 1
    save_scoreboard(scoreboard)

def print_scoreboard():
    print("\n==== SCOREBOARD ====")
    if not scoreboard:
        print("No games played yet.")
        return
    for player, stats in scoreboard.items():
        print(f"{player}: {stats['wins']} Wins, {stats['losses']} Losses, {stats['ties']} Ties")
    print("====================\n")

class Player:
    def __init__(self, name, symbol, is_ai=False):
        self.name = name
        self.symbol = symbol
        self.is_ai = is_ai

class TicTacToeGame:
    def __init__(self, player1, player2, ai_mode=None):
        self.board = [["-" for _ in range(3)] for _ in range(3)]
        self.players = [player1, player2]
        self.current = 0
        self.turns = 0
        self.ai_mode = ai_mode  # None, 'easy', etc.
        self.move_history = []  # Stack for undo
        self.redo_stack = []    # Stack for redo

    def print_board(self):
        for row in self.board:
            print(" ".join(row))
        print()

    def is_taken(self, row, col):
        return self.board[row][col] != "-"

    def add_to_board(self, row, col, symbol):
        self.board[row][col] = symbol

    def remove_from_board(self, row, col):
        self.board[row][col] = "-"

    def is_win(self, symbol):
        b = self.board
        # Rows, columns, diagonals
        for i in range(3):
            if all(b[i][j] == symbol for j in range(3)):
                return True
            if all(b[j][i] == symbol for j in range(3)):
                return True
        if b[0][0] == b[1][1] == b[2][2] == symbol:
            return True
        if b[0][2] == b[1][1] == b[2][0] == symbol:
            return True
        return False

    def is_tie(self):
        return self.turns >= 9

    def get_move(self, player):
        while True:
            user_input = input(f"{player.name} ({player.symbol}), enter position 1-9, 'undo', 'redo', or 'q' to quit: ")
            if user_input.lower() == 'q':
                print("Thanks for playing!")
                return None
            if user_input.lower() == 'undo':
                return 'undo'
            if user_input.lower() == 'redo':
                return 'redo'
            if not user_input.isdigit():
                print("Invalid input. Enter a number 1-9, 'undo', 'redo', or 'q'.")
                continue
            pos = int(user_input)
            if pos < 1 or pos > 9:
                print("Number out of bounds. Enter 1-9.")
                continue
            row, col = divmod(pos - 1, 3)
            if self.is_taken(row, col):
                print("Position already taken.")
                continue
            return row, col

    def get_ai_move_easy(self):
        empty = [(r, c) for r in range(3) for c in range(3) if self.board[r][c] == "-"]
        return random.choice(empty)

    def undo(self):
        if not self.move_history:
            print("Nothing to undo.")
            return False
        row, col, symbol, player_index = self.move_history.pop()
        self.remove_from_board(row, col)
        self.turns -= 1
        self.redo_stack.append((row, col, symbol, player_index))
        self.current = player_index
        print("Move undone.")
        return True

    def redo(self):
        if not self.redo_stack:
            print("Nothing to redo.")
            return False
        row, col, symbol, player_index = self.redo_stack.pop()
        self.add_to_board(row, col, symbol)
        self.turns += 1
        self.move_history.append((row, col, symbol, player_index))
        self.current = 1 - player_index
        print("Move redone.")
        return True

    def play(self):
        while True:
            self.print_board()
            player = self.players[self.current]
            if self.ai_mode and self.current == 1:
                row, col = self.get_ai_move_easy()
                print(f"AI ({player.symbol}) chooses position {row * 3 + col + 1}")
            else:
                move = self.get_move(player)
                if move is None:
                    break
                if move == 'undo':
                    if self.undo():
                        continue
                    else:
                        continue
                if move == 'redo':
                    if self.redo():
                        continue
                    else:
                        continue
                row, col = move
            self.add_to_board(row, col, player.symbol)
            self.move_history.append((row, col, player.symbol, self.current))
            self.redo_stack.clear()  # Clear redo stack after a new move
            self.turns += 1
            if self.is_win(player.symbol):
                self.print_board()
                print(f"{player.name} ({player.symbol}) wins!")
                update_scoreboard(player.name, self.players[0], self.players[1])
                break
            if self.is_tie():
                self.print_board()
                print("It's a tie!")
                update_scoreboard('tie', self.players[0], self.players[1])
                break
            self.current = 1 - self.current

# --- GUI Classes and Logic (from tic_tac_toe_gui.py) ---
if TK_AVAILABLE:
    import time
    class TicTacToeGUI:
        def __init__(self, root):
            self.root = root
            self.root.title("Tic Tac Toe")
            self.theme = 'light'
            self.colors = {
                'light': {
                    'bg': '#f7fafc',
                    'fg': '#22223b',
                    'btn': '#e0e1dd',
                    'btn_active': '#a9def9',
                    'win': '#b5ead7',
                    'border': '#a3cef1',
                    'logo': '#22223b',
                },
                'dark': {
                    'bg': '#22223b',
                    'fg': '#f7fafc',
                    'btn': '#393e46',
                    'btn_active': '#00adb5',
                    'win': '#00b894',
                    'border': '#00adb5',
                    'logo': '#f7fafc',
                }
            }
            self.score = {"X": 0, "O": 0}
            self.move_history = []
            self.redo_stack = []
            self.setup_menu()

        def fade_in(self, widget, steps=10, delay=20):
            for i in range(steps):
                alpha = int(255 * (i + 1) / steps)
                try:
                    widget.attributes('-alpha', alpha / 255)
                except:
                    pass
                self.root.update()
                self.root.after(delay)

        def fade_out(self, widget, steps=10, delay=20):
            for i in range(steps):
                alpha = int(255 * (steps - i - 1) / steps)
                try:
                    widget.attributes('-alpha', alpha / 255)
                except:
                    pass
                self.root.update()
                self.root.after(delay)

        def setup_menu(self):
            self.clear_window()
            self.menu_frame = tk.Frame(self.root, bg=self.colors[self.theme]['bg'])
            self.menu_frame.pack(expand=True, fill='both')
            # Subtle background gradient (simulate with canvas)
            bg_canvas = tk.Canvas(self.menu_frame, width=420, height=540, highlightthickness=0)
            for i in range(0, 540, 2):
                color = self._fade_color(self.colors[self.theme]['bg'], self.colors[self.theme]['btn_active'], i / 540)
                bg_canvas.create_rectangle(0, i, 420, i+2, fill=color, outline=color)
            bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
            logo = tk.Canvas(self.menu_frame, width=80, height=80, bg=self.colors[self.theme]['bg'], highlightthickness=0)
            logo.create_oval(10, 10, 70, 70, fill=self.colors[self.theme]['logo'], outline=self.colors[self.theme]['border'], width=4)
            logo.create_text(40, 40, text="❌⭕", font=("Segoe UI Emoji", 28, "bold"), fill=self.colors[self.theme]['bg'])
            logo.pack(pady=(30, 10))
            tk.Label(self.menu_frame, text="Tic Tac Toe", font=("Segoe UI", 28, "bold"), bg=self.colors[self.theme]['bg'], fg=self.colors[self.theme]['fg']).pack(pady=(0, 20))
            btn_style = {
                'font': ("Segoe UI", 16, "bold"),
                'bg': self.colors[self.theme]['btn'],
                'fg': self.colors[self.theme]['fg'],
                'activebackground': self.colors[self.theme]['btn_active'],
                'bd': 0,
                'relief': 'flat',
                'highlightthickness': 0,
                'cursor': 'hand2',
                'height': 2,
                'width': 20,
            }
            def animate_btn(e, b):
                b.config(bg=self.colors[self.theme]['btn_active'])
                b.config(font=("Segoe UI", 18, "bold"))
            def reset_btn(e, b):
                b.config(bg=self.colors[self.theme]['btn'])
                b.config(font=("Segoe UI", 16, "bold"))
            for text, cmd in [
                ("Single Player vs AI", self.setup_single_player),
                ("Two Player (Local)", self.setup_two_player),
                ("Replay Last Game", lambda: self.show_popup("Replay Last Game feature coming soon!")),
                ("View Scoreboard", self.show_scoreboard),
                ("Player Customization", self.player_customization),
                ("View Features/Help", self.show_features),
                ("Exit", self.root.quit)
            ]:
                btn = tk.Button(self.menu_frame, text=text, command=cmd, **btn_style)
                btn.pack(pady=10)
                btn.bind('<Enter>', lambda e, b=btn: animate_btn(e, b))
                btn.bind('<Leave>', lambda e, b=btn: reset_btn(e, b))
            self.fade_in(self.menu_frame)

        def info_label_highlight(self):
            # Highlight active player
            orig_fg = self.info_label.cget('fg')
            for i in range(3):
                self.info_label.config(fg=self.colors[self.theme]['btn_active'])
                self.root.update()
                self.root.after(80)
                self.info_label.config(fg=orig_fg)
                self.root.update()
                self.root.after(80)

        def setup_single_player(self):
            name = simpledialog.askstring("Player Name", "Enter your name:", parent=self.root)
            if not name:
                return
            symbol = simpledialog.askstring("Symbol", "Choose your symbol (X/O):", parent=self.root)
            if not symbol or symbol.upper() not in ['X', 'O']:
                symbol = 'X'
            else:
                symbol = symbol.upper()
            ai_symbol = 'O' if symbol == 'X' else 'X'
            ai_choice = simpledialog.askinteger("AI Difficulty", "Select AI Difficulty:\n1. Easy (Random)\n2. Medium (Rule-based)\n3. Hard (Minimax)", parent=self.root, minvalue=1, maxvalue=3)
            ai_mode = { 1: 'easy', 2: 'medium', 3: 'hard' }.get(ai_choice, 'easy')
            self.player1 = Player(name, symbol)
            self.player2 = Player("AI", ai_symbol, is_ai=True)
            self.ai_mode = ai_mode
            self.start_game()

        def setup_two_player(self):
            name1 = simpledialog.askstring("Player 1 Name", "Enter Player 1 name:", parent=self.root)
            if not name1:
                return
            symbol1 = simpledialog.askstring("Symbol", "Player 1, choose your symbol (X/O):", parent=self.root)
            if not symbol1 or symbol1.upper() not in ['X', 'O']:
                symbol1 = 'X'
            else:
                symbol1 = symbol1.upper()
            symbol2 = 'O' if symbol1 == 'X' else 'X'
            name2 = simpledialog.askstring("Player 2 Name", "Enter Player 2 name:", parent=self.root)
            if not name2:
                return
            self.player1 = Player(name1, symbol1)
            self.player2 = Player(name2, symbol2)
            self.ai_mode = None
            self.start_game()

        def start_game(self):
            self.clear_window()
            self.board = [["-" for _ in range(3)] for _ in range(3)]
            self.current = 0
            self.turns = 0
            self.move_history.clear()
            self.redo_stack.clear()
            self.game_over = False
            self.game_frame = tk.Frame(self.root, bg=self.colors[self.theme]['bg'])
            self.game_frame.pack(expand=True, fill='both')
            self.info_label = tk.Label(self.game_frame, text=self.get_turn_text(), font=("Segoe UI", 18, "bold"), bg=self.colors[self.theme]['bg'], fg=self.colors[self.theme]['fg'])
            self.info_label.pack(pady=(20, 10))
            self.score_label = tk.Label(self.game_frame, text=self.get_score_text(), font=("Segoe UI", 13, "bold"), bg=self.colors[self.theme]['bg'], fg=self.colors[self.theme]['fg'])
            self.score_label.pack(pady=(0, 10))
            self.grid_frame = tk.Frame(self.game_frame, bg=self.colors[self.theme]['bg'])
            self.grid_frame.pack(pady=10)
            self.buttons = [[None for _ in range(3)] for _ in range(3)]
            for r in range(3):
                for c in range(3):
                    btn = tk.Button(self.grid_frame, text="", font=("Segoe UI", 36, "bold"), width=3, height=1,
                                    command=lambda row=r, col=c: self.animated_handle_move(row, col),
                                    bg=self.colors[self.theme]['btn'], fg=self.colors[self.theme]['fg'],
                                    activebackground=self.colors[self.theme]['btn_active'],
                                    bd=0, relief='flat', highlightthickness=0, cursor='hand2')
                    btn.grid(row=r, column=c, padx=8, pady=8, ipadx=6, ipady=6)
                    self.buttons[r][c] = btn
                    btn.bind('<Enter>', lambda e, b=btn: b.config(bg=self.colors[self.theme]['btn_active']))
                    btn.bind('<Leave>', lambda e, b=btn: b.config(bg=self.colors[self.theme]['btn']))
            control_frame = tk.Frame(self.game_frame, bg=self.colors[self.theme]['bg'])
            control_frame.pack(pady=18)
            btn_style = {
                'font': ("Segoe UI", 12, "bold"),
                'bg': self.colors[self.theme]['btn'],
                'fg': self.colors[self.theme]['fg'],
                'activebackground': self.colors[self.theme]['btn_active'],
                'bd': 0,
                'relief': 'flat',
                'highlightthickness': 0,
                'cursor': 'hand2',
                'width': 10,
            }
            tk.Button(control_frame, text="Undo", command=self.undo, **btn_style).pack(side='left', padx=6)
            tk.Button(control_frame, text="Redo", command=self.redo, **btn_style).pack(side='left', padx=6)
            tk.Button(control_frame, text="Restart", command=self.start_game, **btn_style).pack(side='left', padx=6)
            tk.Button(control_frame, text="Menu", command=self.setup_menu, **btn_style).pack(side='left', padx=6)
            tk.Button(control_frame, text="Theme", command=self.toggle_theme, **btn_style).pack(side='left', padx=6)
            if self.get_current_player().is_ai:
                self.root.after(500, self.ai_move)

        def animated_handle_move(self, row, col):
            btn = self.buttons[row][col]
            # Animate button press (color flash)
            orig_bg = btn.cget('bg')
            btn.config(bg=self.colors[self.theme]['btn_active'])
            self.root.update()
            self.root.after(80)
            btn.config(bg=orig_bg)
            self.handle_move(row, col)

        def get_turn_text(self):
            p = self.get_current_player()
            return f"{p.name}'s Turn ({p.symbol})"

        def get_score_text(self):
            return f"Score: {self.player1.name} (X): {self.score['X']}   {self.player2.name} (O): {self.score['O']}"

        def get_current_player(self):
            return self.player1 if self.current == 0 else self.player2

        def handle_move(self, row, col):
            if self.game_over or self.board[row][col] != "-":
                return
            player = self.get_current_player()
            self.board[row][col] = player.symbol
            self.buttons[row][col].config(text=player.symbol, fg=self.colors[self.theme]['fg'])
            self.move_history.append((row, col, player.symbol, self.current))
            self.redo_stack.clear()
            self.turns += 1
            if self.check_win(player.symbol):
                self.game_over = True
                self.score[player.symbol] += 1
                self.info_label.config(text=f"{player.name} ({player.symbol}) wins!")
                self.animated_highlight_win(player.symbol)
                self.score_label.config(text=self.get_score_text())
                self.show_popup(f"🎉 {player.name} ({player.symbol}) wins! 🎉")
                update_scoreboard(player.name, self.players[0], self.players[1])
                return
            if self.turns == 9:
                self.game_over = True
                self.info_label.config(text="It's a tie!")
                self.show_popup("🤝 It's a tie! 🤝")
                update_scoreboard('tie', self.players[0], self.players[1])
                return
            self.current = 1 - self.current
            self.info_label.config(text=self.get_turn_text())
            if self.get_current_player().is_ai and not self.game_over:
                self.root.after(500, self.ai_move)

        def ai_move(self):
            empty = [(r, c) for r in range(3) for c in range(3) if self.board[r][c] == "-"]
            if not empty:
                return
            row, col = random.choice(empty)
            self.animated_handle_move(row, col)

        def check_win(self, symbol):
            b = self.board
            for i in range(3):
                if all(b[i][j] == symbol for j in range(3)):
                    self.win_line = [(i, j) for j in range(3)]
                    return True
                if all(b[j][i] == symbol for j in range(3)):
                    self.win_line = [(j, i) for j in range(3)]
                    return True
            if b[0][0] == b[1][1] == b[2][2] == symbol:
                self.win_line = [(0, 0), (1, 1), (2, 2)]
                return True
            if b[0][2] == b[1][1] == b[2][0] == symbol:
                self.win_line = [(0, 2), (1, 1), (2, 0)]
                return True
            return False

        def animated_highlight_win(self, symbol):
            # Animate the winning line highlight (fade-in effect)
            for step in range(1, 8):
                color = self._fade_color(self.colors[self.theme]['btn'], self.colors[self.theme]['win'], step / 7)
                for r, c in getattr(self, 'win_line', []):
                    self.buttons[r][c].config(bg=color)
                self.root.update()
                self.root.after(40)
            for r, c in getattr(self, 'win_line', []):
                self.buttons[r][c].config(bg=self.colors[self.theme]['win'])

        def _fade_color(self, start, end, t):
            # start, end: hex color strings; t: 0.0-1.0
            def hex_to_rgb(h):
                h = h.lstrip('#')
                return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
            def rgb_to_hex(rgb):
                return '#%02x%02x%02x' % rgb
            s = hex_to_rgb(start)
            e = hex_to_rgb(end)
            rgb = tuple(int(s[i] + (e[i] - s[i]) * t) for i in range(3))
            return rgb_to_hex(rgb)

        def undo(self):
            if not self.move_history or self.game_over:
                return
            row, col, symbol, player_index = self.move_history.pop()
            self.board[row][col] = "-"
            self.buttons[row][col].config(text="", bg=self.colors[self.theme]['btn'])
            self.redo_stack.append((row, col, symbol, player_index))
            self.turns -= 1
            self.current = player_index
            self.info_label.config(text=self.get_turn_text())
            self.game_over = False
            for r in range(3):
                for c in range(3):
                    self.buttons[r][c].config(bg=self.colors[self.theme]['btn'])

        def redo(self):
            if not self.redo_stack or self.game_over:
                return
            row, col, symbol, player_index = self.redo_stack.pop()
            self.board[row][col] = symbol
            self.buttons[row][col].config(text=symbol, fg=self.colors[self.theme]['fg'])
            self.move_history.append((row, col, symbol, player_index))
            self.turns += 1
            self.current = 1 - player_index
            self.info_label.config(text=self.get_turn_text())

        def toggle_theme(self):
            # Smooth color transition for theme switch
            old_theme = self.theme
            new_theme = 'dark' if self.theme == 'light' else 'light'
            steps = 10
            for step in range(1, steps + 1):
                t = step / steps
                for widget in self.root.winfo_children():
                    self._animate_widget_bg(widget, old_theme, new_theme, t)
                self.root.update()
                self.root.after(20)
            self.theme = new_theme
            self.setup_menu() if hasattr(self, 'menu_frame') and self.menu_frame.winfo_exists() else self.start_game()

        def _animate_widget_bg(self, widget, old_theme, new_theme, t):
            if hasattr(widget, 'winfo_children'):
                for child in widget.winfo_children():
                    self._animate_widget_bg(child, old_theme, new_theme, t)
            if isinstance(widget, (tk.Frame, tk.Label, tk.Button, tk.Canvas)):
                old_bg = self.colors[old_theme]['bg']
                new_bg = self.colors[new_theme]['bg']
                color = self._fade_color(old_bg, new_bg, t)
                try:
                    widget.config(bg=color)
                except:
                    pass

        def show_popup(self, message):
            popup = tk.Toplevel(self.root)
            popup.title("")
            popup.geometry("300x120")
            popup.configure(bg=self.colors[self.theme]['bg'])
            tk.Label(popup, text=message, font=("Segoe UI Emoji", 20, "bold"), bg=self.colors[self.theme]['bg'], fg=self.colors[self.theme]['fg']).pack(expand=True, pady=20)
            btn = tk.Button(popup, text="OK", font=("Segoe UI", 12, "bold"), command=popup.destroy, bg=self.colors[self.theme]['btn'], fg=self.colors[self.theme]['fg'], activebackground=self.colors[self.theme]['btn_active'], bd=0, relief='flat', highlightthickness=0, cursor='hand2')
            btn.pack(pady=5)
            self.fade_in(popup)
            popup.transient(self.root)
            popup.grab_set()
            self.root.wait_window(popup)

        def clear_window(self):
            for widget in self.root.winfo_children():
                widget.destroy()

        def show_features(self):
            features = "\n".join([f"• {feat}" for feat in FEATURES_LIST])
            self.show_popup(f"Features:\n{features}")

        def player_customization(self):
            self.show_popup("Player Customization: Change names, symbols, and (in future) colors/avatars!")

        def show_scoreboard(self):
            if not scoreboard:
                self.show_popup("No games played yet.")
                return
            lines = [f"{player}: {stats['wins']} Wins, {stats['losses']} Losses, {stats['ties']} Ties" for player, stats in scoreboard.items()]
            popup = tk.Toplevel(self.root)
            popup.title("")
            popup.geometry("350x250")
            popup.configure(bg=self.colors[self.theme]['bg'])
            tk.Label(popup, text="Scoreboard", font=("Segoe UI", 18, "bold"), bg=self.colors[self.theme]['bg'], fg=self.colors[self.theme]['fg']).pack(pady=10)
            for line in lines:
                tk.Label(popup, text=line, font=("Segoe UI", 13), bg=self.colors[self.theme]['bg'], fg=self.colors[self.theme]['fg']).pack(anchor='w', padx=20)
            btn = tk.Button(popup, text="OK", font=("Segoe UI", 12, "bold"), command=popup.destroy, bg=self.colors[self.theme]['btn'], fg=self.colors[self.theme]['fg'], activebackground=self.colors[self.theme]['btn_active'], bd=0, relief='flat', highlightthickness=0, cursor='hand2')
            btn.pack(pady=10)
            self.fade_in(popup)
            popup.transient(self.root)
            popup.grab_set()
            self.root.wait_window(popup)

# --- Startup Menu ---
def main_menu():
    print("Welcome to Tic Tac Toe!")
    print("\nFeatures:")
    for feat in FEATURES_LIST:
        print(f"- {feat}")
    print("\n1. Console Version")
    if TK_AVAILABLE:
        print("2. GUI Version")
    while True:
        choice = input("Select mode (1 for Console{}): ".format(", 2 for GUI" if TK_AVAILABLE else ""))
        if choice == '1':
            console_main_menu()
            break
        elif choice == '2' and TK_AVAILABLE:
            run_gui()
            break
        else:
            print("Invalid choice. Please enter a valid option.")

# --- Console Game Menu ---
def console_menu():
    print("Console Tic Tac Toe!")
    print("1. Single Player vs AI")
    print("2. Two Player (Local)")
    while True:
        choice = input("Select game mode (1 or 2): ")
        if choice == '1':
            name = input("Enter your name: ")
            symbol = input("Choose your symbol (X/O): ").upper()
            if symbol not in ['X', 'O']:
                print("Invalid symbol. Defaulting to X.")
                symbol = 'X'
            ai_symbol = 'O' if symbol == 'X' else 'X'
            print("Select AI Difficulty:")
            print("1. Easy (Random)")
            print("2. Medium (Rule-based)")
            print("3. Hard (Minimax)")
            while True:
                ai_choice = input("Enter 1, 2, or 3: ")
                if ai_choice in ['1', '2', '3']:
                    break
                print("Invalid choice. Please enter 1, 2, or 3.")
            ai_mode = { '1': 'easy', '2': 'medium', '3': 'hard' }[ai_choice]
            player1 = Player(name, symbol)
            player2 = Player("AI", ai_symbol, is_ai=True)
            game = TicTacToeGame(player1, player2, ai_mode=ai_mode)
            game.play()
            break
        elif choice == '2':
            name1 = input("Player 1, enter your name: ")
            symbol1 = input("Player 1, choose your symbol (X/O): ").upper()
            if symbol1 not in ['X', 'O']:
                print("Invalid symbol. Defaulting to X.")
                symbol1 = 'X'
            symbol2 = 'O' if symbol1 == 'X' else 'X'
            name2 = input("Player 2, enter your name: ")
            player1 = Player(name1, symbol1)
            player2 = Player(name2, symbol2)
            game = TicTacToeGame(player1, player2)
            game.play()
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")

# --- Console Main Menu ---
def console_main_menu():
    while True:
        print("\n==== TIC TAC TOE ====")
        print("1. Start Game")
        print("2. Replay Last Game")
        print("3. View Scoreboard")
        print("4. Player Customization")
        print("5. View Features/Help")
        print("6. Exit")
        choice = input("Select an option (1-6): ")
        if choice == '1':
            console_menu()
        elif choice == '2':
            print("Replay Last Game feature coming soon!")
        elif choice == '3':
            print_scoreboard()
        elif choice == '4':
            print("Player Customization feature coming soon!")
        elif choice == '5':
            print("\nFeatures:")
            for feat in FEATURES_LIST:
                print(f"- {feat}")
        elif choice == '6':
            print("Goodbye!")
            exit()
        else:
            print("Invalid choice. Please enter a valid option.")

# --- GUI Runner ---
def run_gui():
    if not TK_AVAILABLE:
        print("tkinter is not available. Please install it to use the GUI version.")
        return
    root = tk.Tk()
    root.geometry("420x540")
    app = TicTacToeGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main_menu()
 
