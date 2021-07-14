import sys
from psmon import publish
from psmon.plots import XYPlot,Image, MultiPlot
import numpy as np
import collections
import time

sys.path.append('../common')
import config
import utils
from mpi_data import mpidata

# user parameters
updaterate = 1 # plot-push frequency, measured in "client updates"
class Server(object):
    def __init__(self, nClients):
        self.nClients = nClients
        self.run()
        return
    
    def run(self):
        while (1):
            print('**** New Run ****')
            nClientsInRun = self.nClients
            myplotter = Plotter()
            while nClientsInRun > 0:
                md = mpidata()
                md.recv()
                if md.small.endrun:
                    nClientsInRun -= 1
                else:
                    myplotter.update(md)
            print('**** End Run ****')
        return
    

class Plotter:
    def __init__(self):
        self.nupdate=0
        self.lasttime = None
        
        self.nevents = 0
        self.sum_img = 0
        self.sum_imgThres = 0
        self.sum_imgPhot = 0

    def update(self,md):
        self.nupdate+=1
    
        self.img = md.img
        self.imgThres = md.imgThres
        try:
            self.imgPhot = md.imgPhot
        except:
            self.imgPhot = None
        # sums since last update - this is not the best way as each rank keeps a few events only, so it'll be noisier. 
        # Otherwise we need to send  lot of data though
        self.running_sumimg = md.sum_img
        self.running_sumimgThres = md.sum_imgThres
        
        # sums since running
        self.nevents += md.small.nevents
        self.sum_img += md.sum_img
        self.sum_imgThres += md.sum_imgThres
        if self.imgPhot is not None:
            self.sum_imgPhot += md.sum_imgPhot
        
        #update
        if self.nupdate%config.UPDATERATE==0:
            if self.lasttime is not None:
                print('Client updates {}, Server received {} events, Rate {}'.format(
                    self.nupdate, self.nevents, (self.nevents-self.lastnevents)/(time.time()-self.lasttime)))
            self.lasttime = time.time()
            self.lastnevents = self.nevents
            
            # Plot 1:
            imgThres = Image(self.nupdate, "Current image (thres)", md.imgThres, 
                             xlabel= 'horizontal (pixel)', ylabel= 'vertical (pixel)', aspect_ratio=1)
            imgThres_sum = Image(self.nupdate, "Average image (thres)", self.sum_imgThres/self.nevents, 
                             xlabel= 'horizontal (pixel)', ylabel= 'vertical (pixel)', aspect_ratio=1)
            p1 = MultiPlot(self.nupdate, 'Image', ncols=2)
            p1.add(imgThres)
            p1.add(imgThres_sum)
            
            # Plot 2:
            if self.imgPhot is not None:
                phot = Image(self.nupdate, "Photons", self.imgPhot, 
                                 xlabel= 'horizontal (pixel)', ylabel= 'vertical (pixel)', aspect_ratio=1)
                phot_sum = Image(self.nupdate, "Average photons", self.sum_imgPhot/self.nevents, 
                                 xlabel= 'horizontal (pixel)', ylabel= 'vertical (pixel)', aspect_ratio=1)
                p2 = MultiPlot(self.nupdate, 'Photon', ncols=2)
                p2.add(phot)
                p2.add(phot_sum)
            
            publish.send(config.TOPIC, p1)
            if self.imgPhot is not None:
                publish.send(config.TOPIC+'_PHOT', p2)




