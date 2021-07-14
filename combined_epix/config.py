import logging
import numpy as np

# General config
EXP = 'xpplw3319'
HUTCH = EXP[:3]
CALIBDIR = ''.join(['/cds/data/psdm/', HUTCH, '/', EXP, '/calib/'])
LIVE = False
UPDATERATE_CLIENT = 10 # how many shots to process before pushing to master
UPDATERATE = 2 # in number of client pushes
LOGLVL = logging.DEBUG
TOPIC = 'COMB_EPIX'

# Ana config
PHOT = True # photon plot
ACCUMULATE = True
THRES = -100 # for thresholding the image
PHOTON_ADU = 173.
PIX = 50 # um
