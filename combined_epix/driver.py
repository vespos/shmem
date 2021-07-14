import sys
from server import Server
from worker import Worker
import logging
import argparse

sys.path.append('../common')
import config
import utils
from mpi_data import mpidata

from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
assert size>1, 'At least 2 MPI ranks required'
numClients = size-1

logging.basicConfig(level=config.LOGLVL)
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument('-r', '--run', help="Run number (offline analysis only)", type=int, default=None)
args = parser.parse_args()
run = args.run

if rank==0:
    Server(numClients)
else:
    Worker(run=run)

MPI.Finalize()
