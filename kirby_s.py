#!/usr/bin/env python3
"""
kirby_s - Kirby in Space Pomodoro Timer
A beautiful terminal-based study tool featuring Kirby floating through space
"""

import os
import sys
import time
import random
import signal
import threading
from datetime import datetime, timedelta

# Space color palette
COLORS = {
    'black': '\033[40m',
    'red': '\033[41m',
    'green': '\033[42m',
    'yellow': '\033[43m',
    'blue': '\033[44m',
    'magenta': '\033[45m',
    'cyan': '\033[46m',
    'white': '\033[47m',
    'bright_black': '\033[100m',
    'bright_red': '\033[101m',
    'bright_green': '\033[102m',
    'bright_yellow': '\033[103m',
    'bright_blue': '\033[104m',
    'bright_magenta': '\033[105m',
    'bright_cyan': '\033[106m',
    'bright_white': '\033[107m',
    'reset': '\033[0m',
    'bold': '\033[1m',
    'dim': '\033[2m',
    'italic': '\033[3m',
    'underline': '\033[4m',
    'blink': '\033[5m',
    'reverse': '\033[7m',
    'hidden': '\033[8m',
    'strikethrough': '\033[9m',
    'default': '\033[39m',
    'bg_black': '\033[49m',
    'clear': '\033[2J\033[H'
}

# Space background elements
STARS = ['.', '*', '+', 'x', 'o', 'O', '@']
KIRBY_BODY = """
        ████████
      ██░░░░░░░░██
    ██░░░░░░░░░░░░██
   ██░░░░░░░░░░░░░░██
  ██░░░░░░░░░░░░░░░░██
  ██░░░░░░██░░░░██░░██
  ██░░░░░░░░░░░░░░░░██
   ██░░░░░░░░░░░░░░██
    ██░░░░░░░░░░░░██
      ██░░░░░░░░██
        ████████
"""

KIRBY_BLINK = """
        ████████
      ██░░░░░░░░██
    ██░░░░░░░░░░░░██
   ██░░░░░░░░░░░░░░██
  ██░░░░░░░░░░░░░░░░██
  ██░░████░░░░████░░██
  ██░░░░░░░░░░░░░░░░██
   ██░░░░░░░░░░░░░░██
    ██░░░░░░░░░░░░██
      ██░░░░░░░░██
        ████████
"""

KIRBY_SLEEP = """
        ████████
      ██░░░░░░░░██
    ██░░░░░░░░░░░░██
   ██░░░░░░░░░░░░░░██
  ██░░░░░░░░░░░░░░░░██
  ██░░▓▓▓▓░░░░▓▓▓▓░░██
  ██░░░░░░░░░░░░░░░░██
   ██░░░░░░░░░░░░░░██
    ██░░░░░░░░░░░░██
      ██░░░░░░░░██
        ████████
"""

class SpacePomodoro:
    def __init__(self):
        self.work_time = 25 * 60  # 25 minutes
        self.short_break = 5 * 60  # 5 minutes
        self.long_break = 15 * 60  # 15 minutes
        self.sessions_before_long = 4
        self.current_session = 1
        self.total_sessions = 0
        self.is_working = True
        self.paused = False
        self.running = False
        self.time_remaining = self.work_time
        self.width = os.get_terminal_size().columns
        self.height = os.get_terminal_size().lines
        self.stars = self._generate_stars()
        self.kirby_x = 10
        self.kirby_y = self.height // 2 - 6
        self.frame = 0
        self.blinking = False

    def _generate_stars(self):
        """Generate random star positions"""
        stars = []
        for _ in range(50):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            char = random.choice(STARS)
            color = random.choice([
                COLORS['white'], COLORS['bright_white'], 
                COLORS['bright_yellow'], COLORS['bright_cyan']
            ])
            stars.append((x, y, char, color))
        return stars

    def _clear(self):
        """Clear terminal"""
        print(COLORS['clear'], end='')

    def _move_cursor(self, x, y):
        """Move cursor to position"""
        print(f'\033[{y};{x}H', end='')

    def _draw_stars(self):
        """Draw space background"""
        for x, y, char, color in self.stars:
            if 0 <= x < self.width and 0 <= y < self.height:
                self._move_cursor(x, y)
                print(f"{color}{char}{COLORS['reset']}", end='')

    def _draw_kirby(self, x, y):
        """Draw Kirby at position with animation"""
        self.frame = (self.frame + 1) % 30
        if self.frame % 20 < 2:
            art = KIRBY_BLINK
        elif not self.is_working:
            art = KIRBY_SLEEP
        else:
            art = KIRBY_BODY

        lines = art.strip().split('\n')
        for i, line in enumerate(lines):
            if 0 <= y + i < self.height:
                self._move_cursor(x, y + i)
                colored_line = line.replace('█', f"{COLORS['bright_magenta']}█{COLORS['reset']}")
                colored_line = colored_line.replace('░', f"{COLORS['magenta']}░{COLORS['reset']}")
                colored_line = colored_line.replace('▓', f"{COLORS['bright_red']}▓{COLORS['reset']}")
                print(colored_line, end='')

    def _draw_planet(self, x, y, planet_type):
        """Draw a planet"""
        if planet_type == 0:
            planet = [
                "     .-.",
                "    (   )",
                "   /     \\",
                "  (       )",
                "   \\     /",
                "    (   )",
                "     '-'"
            ]
            color = COLORS['bright_yellow']
        elif planet_type == 1:
            planet = [
                "  .-.",
                " (   )",
                "  '-'"
            ]
            color = COLORS['bright_white']
        else:
            planet = [
                "  \\ | /",
                " --*--",
                "  / | \\"
            ]
            color = COLORS['bright_cyan']

        for i, line in enumerate(planet):
            if 0 <= y + i < self.height:
                self._move_cursor(x, y + i)
                print(f"{color}{line}{COLORS['reset']}", end='')

    def _format_time(self, seconds):
        """Format seconds to MM:SS"""
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins:02d}:{secs:02d}"

    def _draw_progress_bar(self, x, y, width, progress):
        """Draw a progress bar"""
        filled = int(width * progress)
        bar = '█' * filled + '░' * (width - filled)
        color = COLORS['bright_green'] if self.is_working else COLORS['bright_blue']
        self._move_cursor(x, y)
        print(f"{color}{bar}{COLORS['reset']}", end='')

    def _draw_box(self, x, y, width, height, title=""):
        """Draw a box with optional title"""
        self._move_cursor(x, y)
        print(f"{COLORS['bright_cyan']}╔{'═' * (width-2)}╗{COLORS['reset']}", end='')

        for i in range(1, height-1):
            self._move_cursor(x, y + i)
            print(f"{COLORS['bright_cyan']}║{' ' * (width-2)}║{COLORS['reset']}", end='')

        self._move_cursor(x, y + height - 1)
        print(f"{COLORS['bright_cyan']}╚{'═' * (width-2)}╝{COLORS['reset']}", end='')

        if title:
            self._move_cursor(x + 2, y)
            print(f"{COLORS['bright_yellow']}{title}{COLORS['reset']}", end='')

    def _draw_ui(self):
        """Draw the main UI"""
        self._clear()
        self._draw_stars()

        float_offset = int(2 * (1 + (self.frame % 10) / 10))
        self._draw_kirby(self.kirby_x, self.kirby_y + float_offset)
        self._draw_planet(self.width - 20, 5, self.frame % 3)

        box_x = self.width // 2 - 25
        box_y = 3
        box_width = 50
        box_height = 12

        self._draw_box(box_x, box_y, box_width, box_height, " KIRBY SPACE POMODORO ")

        time_str = self._format_time(self.time_remaining)
        status = ">>> FOCUS TIME <<<" if self.is_working else "<<< BREAK TIME >>>"
        session_info = f"Session {self.current_session}/{self.sessions_before_long}"

        self._move_cursor(box_x + box_width//2 - len(time_str)//2, box_y + 3)
        print(f"{COLORS['bold']}{COLORS['bright_white']}{time_str}{COLORS['reset']}", end='')

        self._move_cursor(box_x + box_width//2 - len(status)//2, box_y + 5)
        color = COLORS['bright_green'] if self.is_working else COLORS['bright_blue']
        print(f"{color}{status}{COLORS['reset']}", end='')

        self._move_cursor(box_x + box_width//2 - len(session_info)//2, box_y + 6)
        print(f"{COLORS['bright_yellow']}{session_info}{COLORS['reset']}", end='')

        total_time = self.work_time if self.is_working else (self.long_break if self.current_session % self.sessions_before_long == 0 else self.short_break)
        progress = 1 - (self.time_remaining / total_time)
        self._draw_progress_bar(box_x + 5, box_y + 8, box_width - 10, progress)

        self._move_cursor(box_x + 2, box_y + 10)
        print(f"{COLORS['dim']}Total sessions: {self.total_sessions} | Press 'q' to quit, 'p' to pause{COLORS['reset']}", end='')

        self._move_cursor(box_x + 2, box_y + 11)
        print(f"{COLORS['dim']}[Space] Start/Pause | [R] Reset | [S] Skip{COLORS['reset']}", end='')

        sys.stdout.flush()

    def _timer_thread(self):
        """Background timer thread"""
        while self.running:
            if not self.paused and self.time_remaining > 0:
                time.sleep(1)
                self.time_remaining -= 1

                if self.time_remaining <= 0:
                    self._complete_session()
            else:
                time.sleep(0.1)

    def _complete_session(self):
        """Handle session completion"""
        os.system('afplay /System/Library/Sounds/Glass.aiff')

        if self.is_working:
            self.total_sessions += 1
            self.current_session += 1

            if self.current_session > self.sessions_before_long:
                self.time_remaining = self.long_break
                self.current_session = 1
            else:
                self.time_remaining = self.short_break
        else:
            self.time_remaining = self.work_time

        self.is_working = not self.is_working

    def _handle_input(self):
        """Handle user input"""
        import tty
        import termios
        import select

        old_settings = termios.tcgetattr(sys.stdin)
        try:
            tty.setcbreak(sys.stdin.fileno())

            while self.running:
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    char = sys.stdin.read(1)

                    if char == 'q' or char == 'Q':
                        self.running = False
                    elif char == ' ':
                        self.paused = not self.paused
                    elif char == 'p' or char == 'P':
                        self.paused = not self.paused
                    elif char == 'r' or char == 'R':
                        self.time_remaining = self.work_time if self.is_working else (self.long_break if self.current_session % self.sessions_before_long == 0 else self.short_break)
                    elif char == 's' or char == 'S':
                        self.time_remaining = 0
                        self._complete_session()

        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

    def run(self):
        """Main run loop"""
        self.running = True

        print('\033[?25l', end='')

        timer = threading.Thread(target=self._timer_thread)
        timer.daemon = True
        timer.start()

        input_thread = threading.Thread(target=self._handle_input)
        input_thread.daemon = True
        input_thread.start()

        try:
            while self.running:
                self.width = os.get_terminal_size().columns
                self.height = os.get_terminal_size().lines
                self._draw_ui()
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
        finally:
            print('\033[?25h', end='')
            self._clear()
            print(f"{COLORS['bright_magenta']}Thanks for studying with Kirby!{COLORS['reset']}")
            print(f"Total sessions completed: {self.total_sessions}")

def main():
    """Main entry point"""
    if not sys.stdin.isatty():
        print("Please run this script in a terminal!")
        sys.exit(1)

    print(COLORS['clear'])
    print(f"""
    {COLORS['bright_magenta']}
     _  _  _  _  _  _  _  _  _  _  _  _  _  _  _  _  _  _  _  _  _  _  _  _ 
    ( )( )( )( )( )( )( )( )( )( )( )( )( )( )( )( )( )( )( )( )( )( )( )( )
     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

         ██╗  ██╗██╗██████╗ ██████╗ ██╗   ██╗    ██╗███╗   ██╗
         ██║ ██╔╝██║██╔══██╗██╔══██╗╚██╗ ██╔╝    ██║████╗  ██║
         █████╔╝ ██║██████╔╝██████╔╝ ╚████╔╝     ██║██╔██╗ ██║
         ██╔═██╗ ██║██╔══██╗██╔══██╗  ╚██╔╝      ██║██║╚██╗██║
         ██║  ██╗██║██║  ██║██║  ██║   ██║       ██║██║ ╚████║
         ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝██ ╝███      ╚═╝       ╚═╝╚═╝  ╚═══╝

              ███████╗██████╗  █████╗  ██████╗███████╗
              ██╔════╝██╔══██╗██╔══██╗██╔════╝██╔════╝
              ███████╗██████╔╝███████║██║     █████╗  
              ╚════██║██╔═══╝ ██╔══██║██║     ██╔══╝  
              ███████║██║     ██║  ██║╚██████╗███████╗
              ╚══════╝╚═╝     ╚═╝  ╚═╝ ╚═════╝╚══════╝

     _  _  _  _  _  _  _  _  _  _  _  _  _  _  _  _  _  _  _  _  _  _  _  _ 
    ( )( )( )( )( )( )( )( )( )( )( )( )( )( )( )( )( )( )( )( )( )( )( )( )
     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    {COLORS['reset']}

    {COLORS['bright_cyan']}Welcome to Kirby Space Pomodoro!{COLORS['reset']}
    {COLORS['dim']}Press Enter to start your study session...{COLORS['reset']}
    """)

    input()

    pomodoro = SpacePomodoro()
    pomodoro.run()

if __name__ == "__main__":
    main()
