import numpy as np
import logging

from tqdm import tqdm

from alphazero_general.Arena import Arena
from quoridorV2.QuoridorPlayers import RandomPlayer
from utils import dotdict

from alphazero_general.MCTS import MCTS

from quoridorV2.pytorch.NNet import NNetWrapper as nn
from quoridorV2.QuoridorGame import QuoridorGame as Game, QuoridorGame
import QuoridorUtils

log = logging.getLogger(__name__)


def play_games():
    args = dotdict({
        'numIters': 1000,
        'numEps': 200,  # Number of complete self-play games to simulate during a new iteration.
        'tempThreshold': 15,  #
        'updateThreshold': 0.60,
        # During arena playoff, new neural net will be accepted if threshold or more of games are won.
        'maxlenOfQueue': 200000,  # Number of game examples to train the neural networks.
        'numMCTSSims': 40,  # Number of games moves for MCTS to simulate.
        'arenaCompare': 40,  # Number of games to play during arena play to determine if new net will be accepted.
        'cpuct': 1,

        'checkpoint': './temp/',
        'load_model': False,
        'load_folder_file': ('./dev/models/v0_n9', 'quoridor_n9_v0_nnetv0_torch_checkpoint_1.pth.tar'),
        'numItersForTrainExamplesHistory': 20,

    })
    log.info('Loading %s...', Game.__name__)
    g = Game(9)

    log.info('Loading %s...', nn.__name__)
    nnet = nn(g)
    pnet = nn(g)

    nnet.load_checkpoint(folder='/home/leleco/proj/pfg/models/v0_n9', filename='best.pth.tar')
    pnet.load_checkpoint(folder='/home/leleco/proj/pfg/models/v0_n9', filename='best.pth.tar')

    pmcts = MCTS(g, pnet, args)
    nmcts = MCTS(g, nnet, args)
    log.info('PITTING AGAINST PREVIOUS VERSION')
    arena = Arena(lambda x: np.argmax(pmcts.getActionProb(x, temp=0)),
                  lambda x: np.argmax(nmcts.getActionProb(x, temp=0)), g, g.display)
    pwins, nwins, draws = arena.playGames(4, verbose=True)

    log.info('NEW/PREV WINS : %d / %d ; DRAWS : %d' % (nwins, pwins, draws))


def simulate_search():
    game = QuoridorGame(5)
    board = game.getInitBoard()
    board.plot_board(save=False)

    game_ended = game.getGameEnded(board, 1)
    it = 0
    while game_ended == 0:
        it += 1
        actions = game.getValidActions(board, 1)
        action = np.random.choice(len(actions), p=actions / sum(actions))
        next_s, next_player = game.getNextState(board, 1, action)
        board = game.getCanonicalForm(next_s, next_player)
        game_ended = game.getGameEnded(board, 1)
        board.plot_board(invert_yaxis=(it % 2 == 0))


def get_wall_action(n, x, y, is_vertical):
    shift = 12 if is_vertical else 12 + (n - 1) ** 2

    walls = np.zeros((n - 1, n - 1))
    walls[x][y] = 1
    wall = np.argmax(walls.flatten())
    return shift + wall


def test_moves():
    n = 5
    game = QuoridorGame(n)
    board = game.getInitBoard()
    board.plot_board(save=False)

    player = -1

    print(player, game.getValidActions(board, player))
    board, player = game.getNextState(board, player, 10)
    board.plot_board(save=False)

    wall = get_wall_action(n=n, x=3, y=2, is_vertical=True)
    print(player, game.getValidActions(board, player))
    board, player = game.getNextState(board, player, wall)
    board.plot_board(save=False)

    print(player, game.getValidActions(board, player))

    # # Check flip
    # board = game.getCanonicalForm(board, 1)
    # board.plot_board(save=False)
    # board = game.getCanonicalForm(board, -1)
    # board.plot_board(save=False)


def place_wall_and_print(game, board, x, y, isv=True):
    wall = get_wall_action(n=game.n, x=x, y=y, is_vertical=isv)
    board, player = game.getNextState(board, 1, wall)
    path, length = QuoridorUtils.findPath(board.red_position, (3, board.red_goal), board.v_walls, board.h_walls)
    print('len', length)
    print(board.v_walls)
    print(board.h_walls)
    board.plot_board(path=path, save=False)
    return board


def play_random_moves(n_random_moves):
    n = 5
    game = QuoridorGame(n)
    board = game.getInitBoard()
    board.plot_board(save=False)

    agent = RandomPlayer(game)
    player = 1
    for i in range(n_random_moves):
        action = agent.play(board)
        print(action)
        board, player = game.getNextState(board, 1, action)
        board = game.getCanonicalForm(board, player)
        board.plot_board(invert_yaxis=(i % 2 == 0), save=False)


def main():
    # n = 5
    # game = QuoridorGame(n)
    # board = game.getInitBoard()
    # board.plot_board(save=False)
    #
    # path, length = QuoridorUtils.findPath(board.blue_position, (3, board.blue_goal), board.v_walls, board.h_walls)
    # board.plot_board(path=path, save=False)
    #
    # board = place_wall_and_print(game, board, 1, 2, False)
    # board = place_wall_and_print(game, board, 2, 3, True)
    # board = place_wall_and_print(game, board, 0, 3, True)

    play_random_moves(10)


if __name__ == "__main__":
    main()