import sys
import numpy as np
import time
import psana as ps
import logging

from ImgAlgos.PyAlgos import photons
import psana as ps

from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

sys.path.append('../common')
import config
import utils
from mpi_data import mpidata

logger = logging.getLogger(__name__)


class Worker(object):
    def __init__(self, run=None, rank=None):
        run = 26
        dsname = utils.get_ds(run=run,
                              exp=config.EXP,
                              live=config.LIVE,
                              calib_dir=config.CALIBDIR)
        logger.info('DATASOURCE: {}'.format(dsname))
        
        self.ds = ps.DataSource(dsname)
        
        self.epixs = [ ps.Detector(dn[1]) for dn in ps.DetNames() if dn[1].find('epix')>=0]
        xcoords = np.array([ epix.coords_x(run) for epix in self.epixs])
        ycoords = np.array([ epix.coords_y(run) for epix in self.epixs])
        self.mask =  np.array([ epix.mask(1, calib=True, status=True, central=True, edges=True) for epix in self.epixs])
        ix = ((xcoords.copy()-np.nanmin(xcoords))/config.PIX).astype(int)
        iy = ((ycoords.copy()-np.nanmin(ycoords))/config.PIX).astype(int)
        self.outShape=(ix.max()+1, iy.max()+1)

        self.ind2d = np.ravel_multi_index((ix.flatten(), iy.flatten()), self.outShape)
        #self.norm = np.bincount(ind2d, minlength=(outShape[0]*outShape[1])).reshape(outShape[0], outShape[1])
        self.mask2d = np.bincount(self.ind2d, weights=self.mask.flatten(), 
                                  minlength=(self.outShape[0]*self.outShape[1])).reshape(self.outShape[0], self.outShape[1])
        
        self.run()
        return
    
    def run(self):
        sum_img = 0
        sum_imgThres = 0
        sum_imgPhot = 0
        for run in self.ds.runs():
            neventsInBatch = 0
            neventsInRank = 0
            for nevt,evt in enumerate(self.ds.events()):
                if not config.LIVE:
                    if nevt%(size-1)!=rank-1:
                        continue
                    time.sleep(0.005)
                
                try:
                    img = [det.calib(evt) for det in self.epixs]
                    imgar = np.array(img)
                except:
                    continue
                
                imgAssembled = np.bincount(
                    self.ind2d,
                    weights=imgar.flatten(),
                    minlength=(self.outShape[0]*self.outShape[1])).reshape(self.outShape[0], self.outShape[1])

                imgThres=imgAssembled.copy()
                imgThres[imgThres<config.THRES]=0
                    
                if config.PHOT>0:
                    imgPhot = photons(imgAssembled/config.PHOTON_ADU, self.mask2d.astype(np.uint8))
                
                sum_img += imgAssembled
                sum_imgThres += imgThres
                if config.PHOT>0:
                    sum_imgPhot += imgPhot

                neventsInBatch += 1
                neventsInRank += 1
                if ((nevt!=0)&((neventsInRank)%config.UPDATERATE_CLIENT == 0)):
                    senddata=mpidata()
                    #send full sum.
                    senddata.addarray('sum_img',np.ascontiguousarray(sum_img))
                    senddata.addarray('sum_imgThres',np.ascontiguousarray(sum_imgThres))
                    #send last image.
                    senddata.addarray('img',imgAssembled)
                    senddata.addarray('imgThres',imgThres)
                    if config.PHOT>0:
                        senddata.addarray('sum_imgPhot',np.ascontiguousarray(sum_imgPhot))
                        senddata.addarray('imgPhot',imgPhot)

                    senddata.small.nevents = neventsInBatch
                    senddata.send()
                    #print('sent data',neventsInBatch, neventsInRank, updaterate)
                    #print(imgar.shape, imgThres.shape, sum_img.shape)
                    #print('image std:',img.std(), (imgThres>0).sum())
                    #resetting summed data.
                    sum_img = 0
                    sum_imgThres = 0
                    sum_imgPhot = 0
                    neventsInBatch = 0
            md = mpidata()
            md.endrun()