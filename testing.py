import itertools

class Mastermind:
    def __init__(self, secret_code, colors='ABCDEF', code_length=None):
        """
        Initialize the Mastermind game.
        
        :param secret_code: The secret code to guess (string).
        :param colors: The possible colors (string, default 'ABCDEF').
        :param code_length: The length of the code (default matches length of secret_code).
        """
        self.colors = colors.upper()
        self.code_length = code_length if code_length else len(secret_code)
        self.secret_code = secret_code.upper()
        self.possible_guesses = [
            ''.join(p) for p in itertools.product(self.colors, repeat=self.code_length)
        ]
        self.guesses = []

    def evaluate_guess(self, guess):
        """Evaluates the guess and returns (black_pegs, white_pegs)."""
        black_pegs = sum(a == b for a, b in zip(self.secret_code, guess))
        white_pegs = sum(
            min(self.secret_code.count(c), guess.count(c)) for c in self.colors
        ) - black_pegs
        return black_pegs, white_pegs

    def auto_solver(self):
        """Auto-solve the code using the 2-color alternating pattern strategy."""
        print(f"Secret Code: {self.secret_code}")
        
        # Start with the first alternating pattern (e.g., 'ABAB...')
        guess1 = ''.join([self.colors[0] if i % 2 == 0 else self.colors[1] for i in range(self.code_length)])
        guess2 = ''.join([self.colors[1] if i % 2 == 0 else self.colors[0] for i in range(self.code_length)])
        
        # First guess
        print(f"Guess 1: {guess1}")
        result1 = self.evaluate_guess(guess1)
        print(f"Feedback: {result1[0]} black pegs, {result1[1]} white pegs")
        
        if result1 == (self.code_length, 0):  # Correct guess
            print("Code broken with first guess!")
            return
        
        # Second guess (switch colors)
        print(f"Guess 2: {guess2}")
        result2 = self.evaluate_guess(guess2)
        print(f"Feedback: {result2[0]} black pegs, {result2[1]} white pegs")
        
        if result2 == (self.code_length, 0):  # Correct guess
            print("Code broken with second guess!")
            return

        print("Code could not be broken with two guesses, which should not happen with alternating patterns.")

# Main execution
if __name__ == "__main__":
    colors = input("Enter the possible colors (e.g., ABCDEF): ").strip().upper()
    code_length = int(input("Enter the length of the code (e.g., 8): "))
    secret_code = input(f"Enter the secret code ({code_length} characters from {colors}): ").strip().upper()

    if len(secret_code) != code_length or not all(c in colors for c in secret_code):
        print(f"Error: The secret code must be exactly {code_length} characters long, using letters from {colors}.")
    else:
        game = Mastermind(secret_code, colors=colors, code_length=code_length)
        game.auto_solver()
