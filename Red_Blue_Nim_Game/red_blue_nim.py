import sys

# Define infinite values for alpha-beta pruning
INF = float('inf')

class RedBlueNim:
    def __init__(self, red_marbles, blue_marbles, depth, mode='standard', start='computer'):
        self.red_marbles = red_marbles
        self.blue_marbles = blue_marbles
        self.depth = depth
        self.mode = mode
        self.current_player = start

        # Define move order for standard and misère versions
        self.standard_move_order = [('red', 2), ('blue', 2), ('red', 1), ('blue', 1)]
        self.misere_move_order = [('blue', 1), ('red', 1), ('blue', 2), ('red', 2)]
        self.move_order = self.standard_move_order if self.mode == 'standard' else self.misere_move_order

    def is_terminal(self):
        """Check if the game is over (either pile has 0 marbles)."""
        return self.red_marbles == 0 or self.blue_marbles == 0

    def apply_move(self, pile, num):
        """Apply the move to the game state."""
        if pile == 'red':
            self.red_marbles -= num
        else:
            self.blue_marbles -= num

    def undo_move(self, pile, num):
        """Undo the move from the game state (used for backtracking)."""
        if pile == 'red':
            self.red_marbles += num
        else:
            self.blue_marbles += num

    def get_valid_moves(self):
        """Generate all valid moves based on the current state."""
        valid_moves = []
        for pile, num in self.move_order:
            if pile == 'red' and self.red_marbles >= num:
                valid_moves.append((pile, num))
            elif pile == 'blue' and self.blue_marbles >= num:
                valid_moves.append((pile, num))
        return valid_moves

    def evaluate(self):
        """Evaluation function for Minimax (returns 1 if computer wins, -1 if human wins)."""
        if self.is_terminal():
            return self.red_marbles * 2 + self.blue_marbles * 3 if self.mode == 'standard' else (self.red_marbles * 2 + self.blue_marbles * 3) # place negative in front of result for misere
        return 0  # Game isn't over yet

    def switch_player(self):
        """Switch the current player between human and computer."""
        if self.current_player == 'computer':
            self.current_player = 'human'
        else:
            self.current_player = 'computer'

    def minimax(self, depth, alpha, beta, maximizing_player):
        """Minimax algorithm with Alpha-Beta Pruning."""
        if self.is_terminal() or depth == 0:
            return self.evaluate()

        if maximizing_player:
            max_eval = -INF
            for move in self.get_valid_moves():
                pile, num = move
                self.apply_move(pile, num)
                self.switch_player()

                eval = self.minimax(depth - 1, alpha, beta, False)

                self.undo_move(pile, num)
                self.switch_player()

                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break  # Beta cutoff
            return max_eval
        else:
            min_eval = INF
            for move in self.get_valid_moves():
                pile, num = move
                self.apply_move(pile, num)
                self.switch_player()

                eval = self.minimax(depth - 1, alpha, beta, True)

                self.undo_move(pile, num)
                self.switch_player()

                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break  # Alpha cutoff
            return min_eval

    def computer_move(self):
        """Make the best move for the computer using Minimax with Alpha-Beta Pruning."""
        best_value = -INF
        best_move = None

        for move in self.get_valid_moves():
            pile, num = move
            self.apply_move(pile, num)
            self.switch_player()

            move_value = self.minimax(self.depth, alpha=-INF, beta=INF, maximizing_player=False)

            self.undo_move(pile, num)
            self.switch_player()

            if move_value > best_value:
                best_value = move_value
                best_move = move

        pile, num = best_move
        print(f"Computer removes {num} {pile} marble(s).")
        return best_move

    def human_move(self):
        """Prompt the human player to make a move."""
        while True:
            pile = input("Enter pile (red/blue): ").lower()
            if pile not in ['red', 'blue']:
                print("Invalid pile, please enter 'red' or 'blue'.")
                continue
            num = int(input("Enter number of marbles (1/2): "))
            if num not in [1, 2]:
                print("Invalid number of marbles, please enter 1 or 2.")
                continue
            if (pile == 'red' and num > self.red_marbles) or (pile == 'blue' and num > self.blue_marbles):
                print("Not enough marbles in the pile. Try again.")
                continue
            return pile, num

    def play(self):
        """Play the game until it's over."""
        while not self.is_terminal():
            if self.current_player == 'computer':
                move = self.computer_move()
                self.apply_move(*move)
            else:
                print(f"Current state: Red Marbles: {self.red_marbles}, Blue Marbles: {self.blue_marbles}")
                move = self.human_move()
                self.apply_move(*move)
            self.switch_player()
        
        # Determine the winner based on the game mode
        if self.mode == 'standard':
            if self.current_player == 'computer':
                print(f"Player wins by {self.evaluate()} points!")
                print(f"Computer loses by {self.evaluate()} points!")
            else:
                print(f"Computer wins by {self.evaluate()} points!")
                print(f"Player loses by {self.evaluate()} points!")
        elif self.mode == 'misere':
            if self.current_player == 'computer':
                print(f"Computer wins by {self.evaluate()} points!")
                print(f"Player loses by {self.evaluate()} points!")
            else:
                print(f"Player wins by {self.evaluate()} points!")
                print(f"Computer loses by {self.evaluate()} points!")

# Main entry point
def main():
    if len(sys.argv) < 3:
        print("Usage: red_blue_nim.py <num-red> <num-blue> <depth> <version> <first-player>")
        return

    num_red = int(sys.argv[1])
    num_blue = int(sys.argv[2])
    depth = int(sys.argv[3]) if len(sys.argv) > 3 else float('inf')
    version = sys.argv[4] if len(sys.argv) > 4 else 'standard'
    first_player = sys.argv[5] if len(sys.argv) > 5 else 'computer'
    #depth = int(sys.argv[5]) if len(sys.argv) > 5 else float('inf')

    game = RedBlueNim(num_red, num_blue, depth, version, first_player)
    game.play()

if __name__ == "__main__":
    main()
