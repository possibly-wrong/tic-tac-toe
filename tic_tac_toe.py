import collections
import functools

class TicTacToe:
    """Probabilistic Tic-Tac-Toe game with given rules.

    Attributes:
        win_squares=float('inf'): first to win_squares wins
        win_early=True: True iff win_squares wins before board is full
        win_succeed=False: True iff must win square to win game
        p=1: probability of winning selected square
        n=3: number of rows/columns
    """
    
    def __init__(self, win_squares=float('inf'), win_early=True,
                 win_succeed=False, p=1, n=3):
        self.win_squares = win_squares
        self.win_early = win_early
        self.win_succeed = win_succeed
        self.p = p
        self.n = n
        self.lines = ([[(i, j) for j in range(n)] for i in range(n)] +
                      [[(i, j) for i in range(n)] for j in range(n)] +
                      [[(i, i) for i in range(n)]] +
                      [[(i, n - 1 - i) for i in range(n)]])

    @functools.lru_cache(maxsize=None)
    def board_value(self, board=None, player=1):
        """Return value of board for player's turn."""

        if board is None:
            board = ((0,) * self.n,) * self.n
            
        # Check for immediate win/loss.
        value = self.win_value(board, player)
        if value != 0:
            return value

        # Select best of all possible moves.
        value = -2
        board = [list(row) for row in board]
        for i in range(self.n):
            for j in range(self.n):
                if board[i][j] == 0:

                    # Evaluate losing the square.
                    board[i][j] = -player
                    lose = (self.win_succeed and
                            self.win_value(board, player) == -1)
                    v_lose = (0 if lose else
                              -self.board_value(self.const(board), -player))

                    # Evaluate winning the square.
                    board[i][j] = player
                    v_win = -self.board_value(self.const(board), -player)
                    if lose:

                        # If opponent must win square to win game, then
                        # if we can win with this square, remove infinite
                        # recursion by solving for value.
                        if self.win_value(board, player) == 1:
                            v_lose = self.p / (self.p - 2)
                        else:
                            v_lose = -self.p + (1 - self.p) * self.board_value(
                                self.const(board), player)

                    # Undo move.
                    board[i][j] = 0
                    value = max(value, self.p * v_win + (1 - self.p) * v_lose)
        return value if value > -2 else 0
        
    def win_value(self, board, player):
        """Return +/-1 if immediate win/lose for player, otherwise 0."""
        
        # Check rows, columns, and diagonals.
        for line in self.lines:
            squares = list({board[i][j] for i, j in line})
            if len(squares) == 1 and squares[0] != 0:
                return squares[0] * player

        # Check five or more squares.
        count = collections.Counter(square for row in board for square in row)
        for square in (1, -1):
            if (count[square] >= self.win_squares and
                (self.win_early or count[0] == 0)):
                return square * player
        return 0

    def const(self, board):
        """Convert list of lists to (hashable) tuple of tuples."""
        return tuple(tuple(row) for row in board)

if __name__ == '__main__':
    win_squares = 5
    win_early = True
    win_succeed = True
    p = 0.5
    v = TicTacToe(win_squares, win_early, win_succeed, p).board_value()
    print(p, v)
