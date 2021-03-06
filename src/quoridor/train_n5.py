import numpy as np
import logging
import sys
import coloredlogs

sys.path.append('quoridor/pathfind/build')
from alphazero_general.Coach import Coach

import torch
from alphazero_general.Arena import Arena
from alphazero_general.utils import dotdict

from alphazero_general.MCTSQuoridor import MCTS

from quoridor.pytorch.NNet import NNetWrapper as nn
from quoridor.QuoridorGame import QuoridorGame as Game

log = logging.getLogger(__name__)
coloredlogs.install(level='INFO')  # Change this to DEBUG to see more info.

def play_games(n=5,
               p1='quoridor_n5_v3_nnet_v2_torch_best.pth.tar',
               p2='quoridor_n5_v3_nnet_v2_torch_best.pth.tar',
               folder='/run/media/leleco/4EB5CC9A2FD2A5F9/dev/models/n5_v3/',
               num_games=4, numMCTSSims=100):
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
        'load_model': True,
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


def train(n=5):
    args = dotdict({
        'numIters': 100,
        'numEps': 600,  # Number of complete self-play games to simulate during a new iteration.
        'tempThreshold': 6,  #
        'updateThreshold': 0.60,
        # During arena playoff, new neural net will be accepted if threshold or more of games are won.
        'maxlenOfQueue': 200000,  # Number of game examples to train the neural networks.
        'numMCTSSims': 100,  # Number of games moves for MCTS to simulate.
        'arenaCompare': 40,  # Number of games to play during arena play to determine if new net will be accepted.
        'cpuct': 2.5,
        'cpuct_base': 19652,
        'cpuct_mult': 2,

        'checkpoint': '/run/media/leleco/4EB5CC9A2FD2A5F9/dev/models/n5_v3/100s5niftehnegdraw',
        'load_model': False,
        'load_examples': True,
        'load_folder_file': ('/run/media/leleco/4EB5CC9A2FD2A5F9/dev/models/n5_v3/100s5niftehnegdraw/',
                             'quoridor_n5_v3_nnet_v2_torch_checkpoint_1.pth.tar'),
        'numItersForTrainExamplesHistory': 15,
    })
    nn_args = dotdict({
        'lr': 0.001,
        'dropout': 0.3,
        'epochs': 10,
        'batch_size': 128,
        'cuda': torch.cuda.is_available(),
        'num_channels': 256,
    })

    log.info('Loading %s...', Game.__name__)
    g = Game(n)

    log.info('Loading %s...', nn.__name__)
    nnet = nn(g, nn_args)

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


def main():
    train(5)

    # play_games()


if __name__ == "__main__":
    main()
