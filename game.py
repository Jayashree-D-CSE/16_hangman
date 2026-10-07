import random
from words import WORDS, HINTS
from stats import SessionStats


DIFFICULTIES = {
    "easy": {
        "lives": 8,
        "score_multiplier": 1,
        "hint_penalty": 1,
    },
    "medium": {
        "lives": 6,
        "score_multiplier": 2,
        "hint_penalty": 2,
    },
    "hard": {
        "lives": 4,
        "score_multiplier": 3,
        "hint_penalty": 3,
    },
}


class HangmanGame:
    def __init__(self):
        self.score = 0
        self.streak = 0
        self.stats = SessionStats()

        self.category = "technology"
        self.difficulty = "medium"

        self.secret = ""
        self.guessed = set()
        self.wrong = set()
        self.lives = 6
        self.hint_used = False

    def start_round(self):
        self.secret = random.choice(WORDS[self.category])
        self.guessed.clear()
        self.wrong.clear()

        # Difficulty is applied at the start of every round.
        self.lives = DIFFICULTIES[self.difficulty]["lives"]

        # Hint availability belongs to the current round only.
        self.hint_used = False

    def masked(self):
        return " ".join(
            ch if ch in self.guessed else "_"
            for ch in self.secret
        )

    def won(self):
        return all(ch in self.guessed for ch in set(self.secret))

    def guess(self, letter):
        # Invalid input must not change game state.
        if len(letter) != 1 or not letter.isalpha():
            return "Enter one letter."

        # A letter can affect the round only once.
        if letter in self.guessed or letter in self.wrong:
            return "Already guessed."

        if letter in self.secret:
            self.guessed.add(letter)
            return "Correct."

        self.wrong.add(letter)
        self.lives -= 1
        return "Wrong."

    def use_hint(self):
        if self.hint_used:
            return None

        self.hint_used = True

        penalty = DIFFICULTIES[self.difficulty]["hint_penalty"]
        self.score = max(0, self.score - penalty)

        return HINTS.get(self.secret, "No hint available.")

    def play_round(self):
        self.start_round()

        while self.lives > 0 and not self.won():
            print("\nWord:", self.masked())
            print("Wrong:", " ".join(sorted(self.wrong)) or "-")
            print(
                "Lives:", self.lives,
                "Score:", self.score,
                "Streak:", self.streak,
                "Difficulty:", self.difficulty,
            )

            raw = input("Letter, /hint, or /quit: ").strip().lower()

            # Quit does not complete the round.
            if raw == "/quit":
                return False

            # Hint is handled once here.
            if raw == "/hint":
                hint = self.use_hint()

                if hint is None:
                    print("Hint already used.")
                else:
                    print("Hint:", hint)

                continue

            # All other input goes through guess().
            # Invalid/repeated input does not alter state.
            print(self.guess(raw))

        if self.won():
            self.streak += 1

            multiplier = DIFFICULTIES[self.difficulty]["score_multiplier"]
            round_score = (5 + self.streak) * multiplier
            self.score += round_score

            self.stats.record(True, self.streak)

            print("Solved:", self.secret)
            print("Round score:", round_score)
            return True

        self.streak = 0
        self.stats.record(False, self.streak)

        print("Out of lives. The word was:", self.secret)
        return True

    def run(self):
        print("Hangman Challenge")
        print("A session consists of multiple rounds.")

        while True:
            # Category selection
            print("\nCategories:", ", ".join(WORDS))
            raw = input("Choose category or q: ").strip().lower()

            if raw == "q":
                return

            if raw not in WORDS:
                print("Unknown category.")
                continue

            self.category = raw

            # Difficulty selection
            print("Difficulties:", ", ".join(DIFFICULTIES))
            difficulty = input("Choose difficulty: ").strip().lower()

            if difficulty not in DIFFICULTIES:
                print("Unknown difficulty.")
                continue

            self.difficulty = difficulty

            if not self.play_round():
                return

            again = input("Another round? [y/n]: ").strip().lower()

            if again == "y":
                continue

            if again == "n":
                print("\nFinal score:", self.score)
                print("Rounds played:", self.stats.rounds)
                print("Rounds won:", self.stats.wins)
                print("Best streak:", self.stats.best_streak)
                return

            print("Please enter y or n.")