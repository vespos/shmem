import logging
import psana

def get_ds(run=None, exp=None, live=False, calib_dir=None):
    if not live: # Run from offline data
        hutch = exp[:3]
        exp_dir = ''.join(['/cds/data/psdm/', hutch, '/', exp, '/xtc/'])
        dsname = ''.join(['exp=', exp, ':run=', str(run), ':smd:', 'dir=', exp_dir])
    else: # Run on shared memeory
        dsname = 'shmem=psana.0:stop=no'
        if calib_dir is not None:
            psana.setOption('psana.calib-dir', calib_dir)
    return dsname


def get_logger(level='info'):
    if level=='info':
        logging.basicConfig(level=logging.info)
    elif level=='debug':
        logging.basicConfig(level=logging.DEBUG)
    return logging.getLogger(__name__)
