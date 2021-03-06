import numpy as np
import logging
import sys
import coloredlogs

sys.path.append('quoridor/pathfind/build')
from alphazero_general.Coach import Coach

from alphazero_general.Arena import Arena
from quoridor.QuoridorPlayers import RandomPlayer
from alphazero_general.utils import dotdict

from alphazero_general.MCTSQuoridor import MCTS

from quoridor.pytorch.NNet import NNetWrapper as nn
from quoridor.QuoridorGame import QuoridorGame as Game
import QuoridorUtils

log = logging.getLogger(__name__)
coloredlogs.install(level='INFO')  # Change this to DEBUG to see more info.

def play_games(n=5,
               p1='quoridor_n5_v3_nnet_v2_torch_best.pth.tar',
               p2='quoridor_n5_v3_nnet_v2_torch_best.pth.tar',
               folder='/run/media/leleco/4EB5CC9A2FD2A5F9/dev/models/n5_v3/',
               num_games=4, numMCTSSims=1000):
    args = dotdict({
        'numIters': 1000,
        'numEps': 200,  # Number of complete self-play games to simulate during a new iteration.
        'tempThreshold': 15,  #
        'updateThreshold': 0.60,
        # During arena playoff, new neural net will be accepted if threshold or more of games are won.
        'maxlenOfQueue': 200000,  # Number of game examples to train the neural networks.
        'numMCTSSims': numMCTSSims,  # Number of games moves for MCTS to simulate.
        'arenaCompare': num_games,
        # Number of games to play during arena play to determine if new net will be accepted.
        'cpuct': 2.5,
        'cpuct_base': 19652,
        'cpuct_mult': 2,

        'checkpoint': './temp/',
        'load_model': False,
        'load_folder_file': ('./dev/models/v0_n5', 'quoridor_n5_v2_nnet_v2_torch_best.pth.tar'),
        'numItersForTrainExamplesHistory': 20,

    })
    log.info('Loading %s...', Game.__name__)
    g = Game(n)

    log.info('Loading %s...', nn.__name__)
    nnet = nn(g)
    pnet = nn(g)

    nnet.load_checkpoint(folder=folder, filename=p1)
    pnet.load_checkpoint(folder=folder, filename=p2)

    pmcts = MCTS(g, pnet, args)
    nmcts = MCTS(g, nnet, args)
    log.info('PITTING AGAINST PREVIOUS VERSION')
    arena = Arena(lambda x: np.argmax(pmcts.getActionProb(x, temp=1)),
                  lambda x: np.argmax(nmcts.getActionProb(x, temp=1)), g, g.display)
    pwins, nwins, draws = arena.playGames(args.arenaCompare, verbose=True)

    log.info('NEW/PREV WINS : %d / %d ; DRAWS : %d' % (nwins, pwins, draws))


# def human():
#     g = Game(5)
#
#     # all players
#     # rp = RandomPlayer(g).play
#     # gp = GreedyQuoridorPlayer(g).play
#     hp = HumanQuoridorPlayer(g).play
#
#     # nnet players
#     n1 = nn(g)
#     n1.load_checkpoint('./pretrained_models/othello/pytorch/', '6x100x25_best.pth.tar')
#     args1 = dotdict({'numMCTSSims': 50, 'cpuct': 1.0})
#     mcts1 = MCTS(g, n1, args1)
#     n1p = lambda x: np.argmax(mcts1.getActionProb(x, temp=0))
#
#     if human_vs_cpu:
#         player2 = hp
#     else:
#         n2 = nn(g)
#         n2.load_checkpoint('./pretrained_models/othello/pytorch/', '8x8_100checkpoints_best.pth.tar')
#         args2 = dotdict({'numMCTSSims': 50, 'cpuct': 1.0})
#         mcts2 = MCTS(g, n2, args2)
#         n2p = lambda x: np.argmax(mcts2.getActionProb(x, temp=0))
#
#         player2 = n2p  # Player 2 is neural network if it's cpu vs cpu.
#
#     arena =  Arena(n1p, player2, g, display=Game.display)
#
#     print(arena.playGames(2, verbose=True))

def simulate_search():
    game = Game(5)
    board = game.getInitBoard()
    board.plot(save=False)

    game_ended = game.getGameEnded(board, 1)
    it = 0
    while game_ended == 0:
        it += 1
        actions = game.getValidActions(board, 1)
        action = np.random.choice(len(actions), p=actions / sum(actions))
        next_s, next_player = game.getNextState(board, 1, action)
        board = game.getCanonicalForm(next_s, next_player)
        game_ended = game.getGameEnded(board, 1)
        board.plot(invert_yaxis=(it % 2 == 0))


def get_wall_action(n, x, y, is_vertical):
    shift = 12 if is_vertical else 12 + (n - 1) ** 2

    walls = np.zeros((n - 1, n - 1))
    walls[x][y] = 1
    wall = np.argmax(walls.flatten())
    return shift + wall


def test_moves():
    n = 5
    game = Game(n)
    board = game.getInitBoard()
    board.plot(save=False)

    player = -1

    print(player, game.getValidActions(board, player))
    board, player = game.getNextState(board, player, 10)
    board.plot(save=False)

    wall = get_wall_action(n=n, x=3, y=2, is_vertical=True)
    print(player, game.getValidActions(board, player))
    board, player = game.getNextState(board, player, wall)
    board.plot(save=False)

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
    # print('len', length)
    # print(board.v_walls)
    # print(board.h_walls)
    board.plot(path=path, save=False)
    return board


def action_tostring(action, n):
    pawn_action_translator = {
        0: 'N',
        1: 'S',
        2: 'E',
        3: 'W',
        4: 'JN',
        5: 'JS',
        6: 'JE',
        7: 'JW',
        8: 'JNE',
        9: 'JSW',
        10: 'JNW',
        11: 'JSE',
    }
    if action < 12:
        return 'MOVE ' + pawn_action_translator[action]
    elif action < 12 + (n - 1) ** 2:
        shift = 12
        return 'VWAL x:' + str((action - shift) // (n - 1)) + ' y:' + str((action - shift) % (n - 1))
    else:
        shift = 12 + (n - 1) ** 2
        return 'HWAL x:' + str((action - shift) // (n - 1)) + ' y:' + str((action - shift) % (n - 1))


def play_random_moves(n_random_moves):
    n = 5
    game = Game(n)
    board = game.getInitBoard()

    agent = RandomPlayer(game)
    player = 1
    for i in range(n_random_moves):
        action = agent.play(board)
        # print(action_tostring(action, n))
        board, player = game.getNextState(board, 1, action)
        board = game.getCanonicalForm(board, player)
        board.plot(save=False, print_pm=True)


def train(n=5):
    log = logging.getLogger(__name__)


    args = dotdict({
        'numIters': 1000,
        'numEps': 100,  # Number of complete self-play games to simulate during a new iteration.
        'tempThreshold': 15,  #
        'updateThreshold': 0.60,
        # During arena playoff, new neural net will be accepted if threshold or more of games are won.
        'maxlenOfQueue': 200000,  # Number of game examples to train the neural networks.
        'numMCTSSims': 100,  # Number of games moves for MCTS to simulate.
        'arenaCompare': 40,  # Number of games to play during arena play to determine if new net will be accepted.
        'cpuct': 2.5,
        'cpuct_base': 19652,
        'cpuct_mult': 2,

        'checkpoint': '/run/media/leleco/4EB5CC9A2FD2A5F9/dev/models/n'+str(n)+'_v3/',
        'load_model': False,
        'load_examples': False,
        'load_folder_file': ('/run/media/leleco/4EB5CC9A2FD2A5F9/dev/models/n'+str(n)+'_v3/'
                             'quoridor_n'+str(n)+'_v3_nnet_v2_torch_checkpoint.pth.tar'),
        'numItersForTrainExamplesHistory': 20,
    })

    log.info('Loading %s...', Game.__name__)
    g = Game(n)

    log.info('Loading %s...', nn.__name__)
    nnet = nn(g)

    if args.load_model:
        log.info('Loading checkpoint "%s/%s"...', *args.load_folder_file)
        nnet.load_checkpoint(args.load_folder_file[0], args.load_folder_file[1])
    else:
        log.warning('Not loading a checkpoint!')

    log.info('Loading the Coach...')
    c = Coach(g, nnet, args)

    if args.load_examples:
        log.info("Loading 'trainExamples' from file...")
        c.loadTrainExamples()

    log.info('Starting the learning process 🎉')

    c.learn()


def place_some_walls():
    n = 5
    game = Game(n)
    board = game.getInitBoard()
    # board.plot_board(save=False)

    board, player = game.getNextState(board, 1, 3)
    board, player = game.getNextState(board, 1, 3)
    # board = place_wall_and_print(game, board, 1, 2, False)
    board = place_wall_and_print(game, board, 2, 1, False)
    board = place_wall_and_print(game, board, 0, 1, False)

    board, player = game.getNextState(board, 1, 2)
    board, player = game.getNextState(board, 1, 2)
    board.plot(save=False)


def main():
    # play_random_moves(10)
    # place_some_walls()
    # train(9)

    play_games(num_games=20)


if __name__ == "__main__":
    main()
