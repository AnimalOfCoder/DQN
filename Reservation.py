import numpy as np
import matplotlib.pyplot as plt
import scipy.io as scio

Config = {
    'B': 5,
    'BLX': np.array([[674, 359, 491, 173, 112]]),
    'BLY': np.array([[674, 359, 491, 173, 112]]),
    'BW': np.array([[10000000]]),
    'L': np.array([[1000]]),
    'LX': np.array([[1000]]),
    'LY': np.array([[1000]]),
    'PW': np.array([[46, 30, 30, 30, 30]]),
    'rs': np.array([[-95]])
}

Store = {
    'AL': np.zeros((2,5)), #  allocated resource
    'RE': np.zeros((2,5)), #  reserved resource
    'RQ': np.zeros((2,5)),
    'S': 0, # number of slices
    'Sprio': np.zeros((2,5)),
    'unu': np.ones((1,5)) # unused resource
}

# Config = scio.loadmat('config.mat')
# Store = scio.loadmat('store.mat')

class Reservation:
    def __init__(self):
        pass

    '''
    4个参数
    initialize if it is the first time
    '''
    @staticmethod
    def initialization(s, V, RQQ):
        if s == 1:
            S=1 # number of slices, initially is 0. but latter it is updated by the call
            AL=np.zeros((S,Config['B']))#allocated resource of the slices in each base station
            RE=np.zeros((S,Config['B']))#reserved resource of the slices in each base station
            RQ=np.zeros((S,Config['B']))#the sum achievable rate times QOS of the slices in the base stations
            unu=np.ones((1,Config['B']))#unused resource in each base station
            Sprio=np.zeros((Config['B'],S))# priority of the slices in each base station       
            Store.update({'S':S, 'AL': AL, 'RE': AL, 'RQ': AL, 'unu': unu, 'Sprio': Sprio}) 
        #register slice
        Store['S']= s # updates the number of slices
        temp = Store['AL']
        if s-1 >= temp.shape[0]:
            temp = np.vstack((temp, V))
        else:
            temp[s-1, :] = V
        
        #Store['AL[s, :]=V # register the allocation
        AL = temp
        Store.update({'AL': AL})            
        temp=Store['RQ']
        if s-1 >= temp.shape[0]:
            temp = np.vstack((temp, RQQ))
        else:
            temp[s-1, :] = RQQ
        #Store['AL[s, :]=V # register the allocation
        RQ = temp
        Store.update({'RQ': RQ})
        #update priority, reservation, and unused 
        # updateunu=max(0, Store.unu - self.V)
        # updateunu=min(1, updateunu)
        Store['unu'] = Store['unu'] - V
        Spp=np.zeros((Store['S'], Config['B']))
        Re=np.zeros((Store['S'], Config['B']))
        Tunu=Store['unu']
        for b in range(0, Config['B']):
            for ss in range(0, Store['S']):
                Spp[ss,b] = RQ[ss,b] / sum(RQ[:,b])
                #update reservations of the slices in all base stations
                Re[ss,b]= np.dot(Tunu[0,b], Spp[ss,b])
        Sprio = Spp
        RE = Re
        Store.update({'Sprio': Sprio})
        Store.update({'RE': RE})


    '''
    3个参数
    the slice has send its new resource allocations or new sum achievable rate, so:
    update the unused resource
    '''
    @staticmethod
    def UpdateUnusedResource(s, V_, RQQ_):
        if V_.sum()==0 and RQQ_.sum() > 0:  
                Store['RQ'][s-1,:] = RQQ_
                #update priority of all slices in the base stations coz RR might be changed by either mobility or
                #changing number of users in others
                for b in range(0, Config['B']):
                    for ss in range(0, Store['S']):
                        Store['Sprio'][ss, b] = Store['RQ'][ss,b] / sum(Store['RQ'][:,b])
                        #update reservations of the slices in all base stations
                        Store['RE'][ss, b] = np.dot(Store['unu'][0,b], Store['Sprio'][ss,b])
        elif V_.sum() >= 0 and RQQ_.sum() == 0:
            # updateunu = max(0, Store['unu']-(V_ - Store['AL'][s-1,:]))
            # updateunu = min(1, updateunu)
            Store['unu'] = Store['unu']-(V_ - Store['AL'][s-1,:])
            #update virtual resource allocation of the slice with the
            #specified slice number.
            Store['AL'][s-1,:] = V_
            for ss in range(0, Store['S']):
                Store['RE'][ss,:] = Store['unu'] * Store['Sprio'][ss,:] # update their reservations
        else:
            print('incorrect request')



    '''
    5个参数
    send network configuration to the slice
    '''
    @staticmethod
    def generateConfigToSlice():
        rs = -95 # thermal noise power the same for all users dBm
        L = 1000 # packet length
        BW = 10000000 # system bandwidth
        B = 5 # total base stations
        MB = 1 # number of macro base stations
        PW = np.array([46, 30, 30, 30, 30])# power of base stations

        # both sides of the coverage area in meteres x axis and y axis
        LX=1000
        LY=1000
        #location matrix of the base stations in the LXxLY area
        #location matrix of the base stations in the x axis of the AXxAY area
        #BLX=500BLY=500
        #BLX is the locations actions of the base stations in the x axis, BLY is in the y axis
        BLX=np.array([[500, 100, 100, 900, 900]])
        BLY=np.array([[500, 100, 900, 100, 900]])
        # these are chosen locations for the five base stations. if you want to generate random locations, commnet this line and uncomment the next two lins
        #BLX=randi([0 LX],1,B) #LX is x axis, we multiply the result by LX to update the value have value upto the value of the coordinates.
        #BLY=randi([0 LY],1,B) #LY is y axis, we multiply the result by LY to update the value have value upto the value of the coordinates.
        

        # todo
        # if(showBS):
        #     plt.plot(BLX, BLY,'*r')
        #     plt.title('location of the base stations')
        #     plt.show()  
            
            
        '''
        if congigurations is asked for the first time, generate the distance matrix 
        and save them for the next time not to be regenerated
        '''
        #BLX=randi([0 LX],1,B) #LX is x axis, we multiply the result by LX to update the value have value upto the value of the coordinates.
        #location matrix of the base stations in the y axis of the AXxAY area
        #BLY=randi([0 LY],1,B) #LY is y axis, we multiply the result by LY to update the value have value upto the value of the coordinates.
        Config.update({'rs': rs, 'L': L, 'BW': BW, 'B': B, 'PW': PW, 'LX': LX, 'LY': LY, 'BLX': BLX, 'BLY': BLY})
        S=rs
        unu=L
        AL=BW
        RE=B # unu= unused resource percentage in the base stations
        if (Config['B'] !=B or Config['LX'] != LX) or Config['LY'] != LY or Config['BW'] != BW:
            # if any of these is updated generate new BS locations matrix and save them
            #BLX=randi([0 LX],1,B) #LX is x axis, we multiply the result by LX to update the value have value upto the value of the coordinates.
            #location matrix of the base stations in the y axis of the AXxAY area
            #BLY=randi([0 LY],1,B) #LY is y axis, we multiply the result by LY to update the value have value upto the value of the coordinates.
            Config.update({'rs': rs, 'L': L, 'BW': BW, 'B': B, 'PW': PW, 'LX': LX, 'LY': LY, 'BLX': BLX, 'BLY': BLY})
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
        if Store['S'] == 0: 
            S = 0
            unu = np.ones((1, Config['B']))#unused resource in each base station
            print('created but empty')
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
    
    @staticmethod
    def sendCurrAllocAndReservOfSlice(s):
        # send the current allocation and reservation of the slice with the specified slice number.
        S = Store['S']
        unu = Store['unu']
        AL = Store['AL'][s-1,:]
        RE = Store['RE'][s-1,:]

        return S, unu, AL, RE
    '''
    2个参数
    slice is leaving the network, delete all information of the slice 
    from the memory and update the reservation of the other slices, 
    if no other slices left clear the file.
    '''
    @staticmethod
    def deleteSlice(s):
        Store['unu'] = Store['unu'] + Store['AL'][s-1,:] #unused resource in each base station      
        Store['AL'][s-1,:] = np.zeros(1,Config['B']) 
        Store['RQ'][s-1,:] = np.zeros(1,Config['B']) #the sum achievable rate times QOS of the slices in the base stations
        if sum(sum(Store['RQ'])) == 0:
            # reset 'Store'
            Store.update({
                'AL': np.zeros((2,5)),
                'RE': np.zeros((2,5)),
                'RQ': np.zeros((2,5)),
                'S': 0,
                'Sprio': np.zeros((2,5)),
                'unu': np.ones((1,5))
            })
            print('——————————————————————Store clear——————————————————————————————')
        else:
            for b in range(0, Config['B']):
                for ss in range(0, Store['S']):
                    Store['Sprio'][ss,b] = Store['RQ'][ss,b] / sum(Store['RQ'][:,b])
                    # update reservations of the slices in all base stations
                    Store['RE'][ss,b] = np.dot(Store['unu'][0,b], Store['Sprio'][ss,b])
           

    
    