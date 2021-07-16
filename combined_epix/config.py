import logging
import numpy as np

# General config
EXP = 'xpplw3319'
HUTCH = EXP[:3]
CALIBDIR = ''.join(['/cds/data/psdm/', HUTCH, '/', EXP, '/calib/'])
LIVE = False
UPDATERATE_CLIENT = 10 # how many shots to process before pushing to master
UPDATERATE = 2 # visualization update (in number of client pushes)
LOGLVL = logging.DEBUG
TOPIC = 'COMB_EPIX'

# Ana config
PHOT = True # photon plot
RUNNING_AVERAGE = 10 # In mulitple of UPDATERATE_CLIENT. Set to 0 for infinite average
THRES = 40 # Pixel threshold
PHOTON_ADU = 173. # for photonizing
PIX = 50 # um
