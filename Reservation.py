import numpy as np
import matplotlib.pyplot as plt
import scipy.io as scio


Config = scio.loadmat('config.mat')
Store = scio.loadmat('store.mat')

class Reservation:
    def __init__(self, s, V, RQQ):
        self.s = s
        self.V = V
        self.RQQ = RQQ
    
    '''
    5个参数
    send network configuration to the slice
    '''
    def generateConfigToSlice():
        rs = -95 # thermal noise power the same for all users dBm
        L = 1000 # packet length
        BW = 10000000 # system bandwidth
        B = 5 # total base stations
        MB = 1 # number of macro base stations
        PW = np.hstack((46 * np.ones((1,1)), 30 * np.ones((1,4))))# power of base stations

        # both sides of the coverage area in meteres x axis and y axis
        LX=1000
        LY=1000
        #location matrix of the base stations in the LXxLY area
        #location matrix of the base stations in the x axis of the AXxAY area
        #BLX=500BLY=500
        #BLX is the locations actions of the base stations in the x axis, BLY is in the y axis
        BLX=np.array([500, 100, 100, 900, 900])
        BLY=np.array([500, 100, 900, 100, 900])
        # these are chosen locations for the five base stations. if you want to generate random locations, commnet this line and uncomment the next two lins
        #BLX=randi([0 LX],1,B) #LX is x axis, we multiply the result by LX to update the value have value upto the value of the coordinates.
        #BLY=randi([0 LY],1,B) #LY is y axis, we multiply the result by LY to update the value have value upto the value of the coordinates.
        
        plt.plot(BLX,BLY,'*r')
        plt.title('location of the base stations')
        plt.show()  
            
            
        if Config['file'] != 2:
            '''
            if congigurations is asked for the first time, generate the distance matrix 
            and save them for the next time not to be regenerated
            '''
        #BLX=randi([0 LX],1,B) #LX is x axis, we multiply the result by LX to update the value have value upto the value of the coordinates.
        #location matrix of the base stations in the y axis of the AXxAY area
        #BLY=randi([0 LY],1,B) #LY is y axis, we multiply the result by LY to update the value have value upto the value of the coordinates.
            scio.savemat('config.mat', {'rs': rs, 'L': L, 'BW': BW, 'B': B, 'PW': PW, 'LX': LX, 'LY': LY, 'BLX': BLX, 'BLY': BLY})
            S=rs
            unu=L
            AL=BW
            RE=B # unu= unused resource percentage in the base stations
        elif (Config['B'] !=B or Config['LX'] != LX) or Config['LY'] != LY or Config['BW'] != BW:
            # if any of these is updated generate new BS locations matrix and save them
            #BLX=randi([0 LX],1,B) #LX is x axis, we multiply the result by LX to update the value have value upto the value of the coordinates.
            #location matrix of the base stations in the y axis of the AXxAY area
            #BLY=randi([0 LY],1,B) #LY is y axis, we multiply the result by LY to update the value have value upto the value of the coordinates.
            scio.savemat('config.mat', {'rs': rs, 'L': L, 'BW': BW, 'B': B, 'PW': PW, 'LX': LX, 'LY': LY, 'BLX': BLX, 'BLY': BLY})
            S=rs
            unu=L
            AL=BW
            RE=B
        else:
            # don't regenerate the distance matrix, they must be fixed for all slices
            BLX=Config['BLX']
            BLY=Config['BLY']
            S=rs
            unu=L
            AL=BW
            RE=B
        
        return S,unu,AL,RE,PW,LX,LY,BLX,BLY
    
    '''
    0个参数 
    send unused resource vector and the number of slices. 
    i.e the index of the last slice number for other sllices to be appended. 
    this is for new slices that wants to know the available resource for admission control and initialization
    '''
    @staticmethod
    def getUnusedResourceAndNumOfSlices():
        if Store['file'] != 2:
            S = 0
            unu = np.ones(1, Config['B'])#unused resource in each base station
            #fprintf('to be created\n')
        elif Store['S'] == 0:
            S = 0
            unu = np.ones(1, Config['B'])#unused resource in each base station
            #fprintf('created but empty\n')
        else:
            unu = Store['unu']
            S = Store['S']
        return S, unu
        ######
        #i will improve it by adding context blocking to prevent
        #more than one admission control at the same time. it must
        #refuse to send resource information untill the current slice
        #finishes admission decision


    '''
    1个参数
    send the current allocation and reservation of the slice with the specified slice number.
    '''
    def sendCurrAllocAndReservOfSlice(self):
        # send the current allocation and reservation of the slice with the specified slice number.
        S = Store['S']
        unu = Store['unu']
        AL = Store['AL'][self.s,:]
        RE = Store['RE'][self.s,:]

        return S, unu, AL, RE
    '''
    2个参数
    slice is leaving the network, delete all information of the slice 
    from the memory and update the reservation of the other slices, 
    if no other slices left clear the file.
    '''
    def deleteSlice(self):
        Store['unu'] = Store['unu'] + Store['AL'][self.s,:] #unused resource in each base station      
        Store['AL'][self.s,:] = np.zeros(1,Config['B']) 
        Store['RQ'][self.s,:] = np.zeros(1,Config['B']) #the sum achievable rate times QOS of the slices in the base stations
        if sum(sum(Store['RQ'])) == 0:
            # delete 'store.mat'
            print('——————————————————————Store.mat clear——————————————————————————————')
        else:
            for b in range(0, Config['B']):
                for ss in range(0, Store['S']):
                    Store['Sprio'][ss,b] = Store['RQ'][ss,b] / sum(Store['RQ'][:,b])
                    # update reservations of the slices in all base stations
                    Store['RE'][ss,b] = np.dot(Store['unu'][0,b], Store['Sprio'][ss,b])
           

    '''
    3个参数
    the slice has send its new resource allocations or new sum achievable rate, so:
    update the unused resource
    '''
    def UpdateUnusedResource(self):
        if sum(self.V)==0 and sum(self.RQQ) > 0:  
                Store['RQ'][self.s,:] = self.RQQ
                #update priority of all slices in the base stations coz RR might be changed by either mobility or
                #changing number of users in others
                for b in range(0, Config['B']):
                    for ss in range(0, Store['S']):
                        Store['Sprio'][ss, b] = Store['RQ'][ss,b] / sum(Store['RQ'][:,b])
                        #update reservations of the slices in all base stations
                        Store['RE'][ss, b] = np.dot(Store['unu'][0,b], Store['Sprio'][ss,b])
        elif sum(self.V) >= 0 and sum(self.RQQ) == 0:
            updateunu = max(0, Store['unu']-(self.V - Store['AL'][self.s,:]))
            updateunu = min(1, updateunu)
            Store['unu'] = updateunu
            #update virtual resource allocation of the slice with the
            #specified slice number.
            Store['AL'][self.s,:] = self.V
            for ss in range(0, Store['S']):
                Store['RE'][ss,:] = Store['unu'] * Store['Sprio'][ss,:] # update their reservations
        else:
            print('incorrect request')

    '''
    4个参数
    initialize if it is the first time
    '''
    def initialization(self):
        if self.s == 1:
            S=1 # number of slices, initially is 0. but latter it is updated by the call
            AL=np.zeros(S,Config['B'])#allocated resource of the slices in each base station
            RE=np.zeros(S,Config['B'])#reserved resource of the slices in each base station
            RQ=np.zeros(S,Config['B'])#the sum achievable rate times QOS of the slices in the base stations
            unu=np.ones(1,Config['B'])#unused resource in each base station
            Sprio=np.zeros(Config['B'],S)# priority of the slices in each base station       
            scio.savemat('store.mat',{'S':S, 'AL': AL, 'RE': AL, 'RQ': AL, 'unu': unu, 'Sprio': Sprio}) 
        #register slice
        Store['S']= self.s # updates the number of slices
        temp = Store['AL']
        temp[self.s, :] = self.V
        #Store['AL[s, :]=V # register the allocation
        AL = temp
        scio.savemat('store.mat', {'AL': AL})            
        temp=Store['RQ']
        temp[self.s, :] = self.RQQ
        #Store['AL[s, :]=V # register the allocation
        RQ = temp
        scio.savemat('store.mat', {'RQ': RQ})
        #update priority, reservation, and unused 
        updateunu=max(0, Store['unu-V'])
        updateunu=min(1, updateunu)
        Store['unu'] = updateunu
        Spp=np.zeros(Store['S'], Config['B'])
        Re=np.zeros(Store['S'], Config['B'])
        Tunu=Store['unu']
        for b in range(0, Config['B']):
            for ss in range(0, Store['S']):
                Spp[ss,b] = RQ[ss,b] / sum(RQ[:,b])
                #update reservations of the slices in all base stations
                Re[ss,b]= np.dot(Tunu(0,b), Spp[ss,b])
        Sprio = Spp
        RE = Re
        scio.savemat('store.mat', {'Sprio': Sprio})
        scio.savemat('store.mat', {'RE': RE})

