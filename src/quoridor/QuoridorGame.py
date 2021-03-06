import sys
import os

import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), 'pathfind/build'))

from alphazero_general.Game import Game
from .QuoridorLogic import QuoridorBoard


class QuoridorGame(Game):
    def __init__(self, n):
        super().__init__()
        self.n = n
        self.action_size = 12 + 2 * (self.n - 1) ** 2
        self.board_len = 2 * self.n - 1

    def __str__(self):
        return 'quoridor_n' + str(self.n) + '_v3'

    def getInitBoard(self):
        """
        Returns:
            startBoard: a representation of the board (ideally this is the form
                        that will be the input to your neural network)
        """
        return QuoridorBoard(self.n)

    def getActionSize(self):
        """
        Returns:
            actionSize: number of all possible actions
        """
        # 4 pawn moves, 8 jumps, 64 vertical walls, 64 horizontal walls
        return self.action_size

    def getBoardSize(self):
        return (self.n, self.n, 2), (self.n - 1, self.n - 1, 2), 17

    def getNextState(self, board, player, action):
        """
        Input:
            board: current board
            player: current player (1 or -1)
            action: action taken by current player

        Returns:
            nextBoard: board after applying action
            nextPlayer: player who plays in the next turn (should be -player)
        """
        next_board = QuoridorBoard(self.n, board=board)
        next_board.executeAction(player, action)
        return next_board, -player

    def getValidActions(self, board, player):
        """
        Input:
            board: current board
            player: current player

        Returns:
            validMoves: a binary vector of length self.getActionSize(), 1 for
                        moves that are valid from the current board and player,
                        0 for invalid moves
        """
        return board.getValidActions(player)

    def getGameEnded(self, board, player):
        """
        Input:
            board: current board
            player: current player (1 or -1)

        Returns:
            r: 0 if game has not ended. 1 if player won, -1 if player lost,
               small non-zero value for draw.

        """
        return board.getGameEnded(player)

    def getCanonicalForm(self, board, player):
        """
        Input:
            board: current board
            player: current player (1 or -1)

        Returns:
            canonicalBoard: returns canonical form of board. The canonical form
                            should be independent of player. For e.g. in chess,
                            the canonical form can be chosen to be from the pov
                            of white. When the player is white, we can return
                            board as is. When the player is black, we can invert
                            the colors and return the board.
        """
        next_board = QuoridorBoard(self.n, board=board)
        return next_board.makeCanonical(player)

    def getSymmetries(self, board, pi):
        """
        Input:
            board: current board
            pi: policy vector of size self.getActionSize()

        Returns:
            symmForms: a list of [(board,pi)] where each tuple is a symmetrical
                       form of the board and the corresponding pi vector. This
                       is used when training the neural network from examples.
        """
        pawn_moves = 12
        vwa_size = pawn_moves + (self.n - 1) ** 2
        vw_actions = list(np.flipud(np.array(pi[pawn_moves:vwa_size]).reshape(self.n - 1, self.n - 1)).flatten())
        hw_actions = list(np.flipud(np.array(pi[vwa_size:]).reshape(self.n - 1, self.n - 1)).flatten())
        pi2 = pi[:12] + vw_actions + hw_actions

        pi2[2], pi2[3] = pi2[3], pi2[2]
        pi2[6], pi2[7] = pi2[7], pi2[6]
        pi2[8], pi2[10] = pi2[10], pi2[8]
        pi2[9], pi2[11] = pi2[9], pi2[11]
        return [(board.getBoard(), pi), (board.getBoardFlippedHorizontally(), pi2)]

    def stringRepresentation(self, board):
        """
        Input:
            board: current board

        Returns:
            boardString: a quick conversion of board to a string format.
                         Required by MCTS for hashing.
        """
        return board.getBoardHashable()

    def display(self, board, name=None, save_folder=None, save=True):
        board.plot(name=name, save_folder=save_folder, save=save)
