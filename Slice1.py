import numpy as np
from Reservation import Reservation
from DQNd import DQNd 
from BS import BS
from Delay_ADMM_Alloc import Delay_ADMM_Alloc 
# DELAY BASED
class Slice1:
    def __init__(self, s1, v, P11, ii, rt, Dc, ar, du, ru, cng1, AL1, RE1):
        #read network configurations
        # rt is normalized achievable data rate of the users of slice 1
        # Dc is the delay constraint of slice1 
        # ar is the arrival rate of slice1
        # P1 is the relative priorities of the base stations to slice21
        # du is a vector of QoS utility of of users of slice 2. delay utility . equation 4
        # ru is a vecor of the resource utility of users of slice1. equation 8
        # v2 is the updated resource of slice1 after the action given by DQNd. the
        # function of resource updater program is BS.update_AL_pro.m. it uses equation 23-25
        # a1 is the action for slice1 by DQNd
        # d1 is the delay exprienced after ADMM.
        # s1 is ID of slice1(also user number)
        # P11 is same as P1
        # ii is the current iteration or the slicing time of the system. 
        # cng1 is an indicator variable that tells whether the number of users of
        # the slice1 is changed or not. but not used in this file, it is used in the other files. it was here in previous
        # design.
        # AL1 is the vector of allocated users to slice1
        # RE1 is the vector of reserved users of slice1
        self.s1 = s1
        self.v = v
        self.P11 = P11
        self.ii = ii 
        self.rt = rt 
        self.Dc = Dc 
        self.ar = ar 
        self.du = du 
        self.ru = ru 
        self.cng1 = cng1 
        self.AL1 = AL1 
        self.RE1 = RE1


    '''
    1个参数
    create the network, and make channels, initialize neural network
    '''
    @staticmethod
    def initSlice(s1):    
        rs, L, BW, B, PW, LX, LY, BLX, BLY = Reservation.generateConfigToSlice()
        K1 = s1 # number of users of slice1
        Dc = 0.1 * np.ones((1, K1)) # delay constraint of slice1
        #location matrix of the users of the slice in the LXxLY area
        #location matrix of the users in the x axis of the AXxAY area
        ULX1 = np.random.randint(0, LX, (1, K1)) #LX is x axis, we multiply the result by LX to update the value have value upto the value of the coordinates.
        #location matrix of the users in the y axis of the AXxAY area
        ULY1 = np.random.randint(0, LY,(1, K1)) #LY is y axis, we multiply the result by LY to update the value have value upto the value of the coordinates.
        #distance matrix of the users to the base stations
        DKB1 = np.zeros((K1,B))
        
        for k in range(0, K1):
            for b in range(0, B):
                x1 = np.array([ULX1[0,k], ULY1[0,k]])
                x2 = np.array([BLX[0,b], BLY[0,b]])
                dist = np.linalg.norm(x1 - x2)
                DKB1[k,b] = max(dist,1) # distane between BS and user, assume minimum 1m.
        # arrival rate of users
        ar = 80 + np.random.randint(0, 40,(1, K1))

        # power multiply by channel gain(received power)
        pg = np.zeros((K1,B))
        for i in range(0, K1): # users
            for j in range(0, B): # base stations
                '''
                the Channel Gain is equivalent to the inverse of sum of the losses.
                linear division is subtraction in decibels.(if it was division in linear, it will be subtraction in decibel becuase of logarithm)
                the randn with deviation of 8 is for shadowing. the randi is for antena gain
                '''
                pg[i,j] = PW[j] - (34 + 40 * np.log10(DKB1[i,j]) + 8 * np.random.randn())# received at the user from base station, in other words transmitted power times channel gain
                
        #Achievable data rate of users on each base station
        R = np.zeros((K1, B))
        for i in range(0, K1):
            for j in range(0, B):
                R[i,j]=BW * np.log2(1+(np.power(10, pg[i,j]/10) / (sum(np.power(10, pg[i,:] / 10)) - np.power(10, pg[i,j]/10) + np.power(10, rs / 10))))
         
        #normalized achiecable datarate of users on each base station
        rt = R / L
        # do all the code below iteratively at every specified time 
        #virtual resouce
        #create the deep Q network
        #DQNd()
        du=0
        ru=0# out side the iteration

        # todo
        # dqn1 = DQNd()
        # dqn1.createNN()

        P1 = np.zeros((1,B))
        v = np.zeros((1,B))
        a1 = 0
        d1 = -1

        return rt,Dc,ar,P1,du,ru

    '''
    12个参数
    make resource managemet
    ''' 
    def makeResourceManagement(self, RL):
        P1=self.P11
        (K1a,B)=np.array(self.rt).shape
        a1 = 0
        if self.ii <= 0: #we use ii=0 to differenciate whether the resource managment is form DQN or NVS and Netshare. bcz only DQN uses the neural network but the other algoriths does not need the neural network
            print('this will not be used for training becuase it is from NVS or NetShare') 
            v=self.v
        elif self.ii == 1: 
            # initially user random action or use the whole reservation
            # becuase you have not state information and allocation
            a1=1 #randi([-9 10],1,1)/10
            v=BS.update_AL_pro(np.zeros((1,B)), self.RE1,P1,a1)
            Reservation.UpdateUnusedResource(self.s1,v,np.array([0]))# send  resource update to the base stations
            
        elif self.ii>1:# use the neural network for dynamic resource management
            a1 = RL.choose_action([sum(self.AL1 * P1),sum(self.du)/K1a,sum(self.ru)/K1a,sum(self.RE1 * P1)])
            v = BS.update_AL_pro(self.AL1, self.RE1,P1,a1)
            Reservation.UpdateUnusedResource(self.s1,v,np.array([0]))# send  resource update to the base stations  
             

        if np.sum(v)==0:# if resource for the slice is 0, the allocation to users is also 0
            d1 = -1 * np.ones((1, np.array(self.rt).shape[0]))   
            r1 = np.zeros(np.array(self.rt).shape[0], 1)
        else:# ADMM
            rrr=self.rt
            y = Delay_ADMM_Alloc.ADMM_Alloc(v, self.ar, self.rt, self.Dc)
            rt = rrr
            yR = y * rt
            # sum rate of users
            r1 = np.sum(yR, axis=1)
            # delay of the users
            d1 = -1 * np.ones((1,K1a))
            for i in range(0, K1a):
                d1[0,i] = 1 / (r1[i] - self.ar[0, i])
            
        delay = d1 #show the delay
        min_max_D=[min(d1), max(d1)]# show the minimum delay and the maximum delay out of all the users of the slice
        #calculate new resource utilization and QoS utility of next state
        #cululate  delay utility for delay 100 ms upper bound
        dd = d1*1000#change to ms
        ndu=np.zeros((1,K1a))
        nru=np.zeros((1,K1a))
        for uk1 in range(0,K1a):
            if dd[0,uk1]<0 or dd[0,uk1] > self.Dc[0,uk1]*1000: 
                ndu[0,uk1]=0
                nru[0,uk1]=0
            else:
                ndu[0,uk1]= -0.5 * np.tanh(0.06 * (dd[0,uk1]-70)) + 0.5 
                nru[0,uk1]=min(1,(self.ar[0,uk1] + 1 / self.Dc[0,uk1]) / r1[uk1])

        du=ndu
        ru=nru

        
        return P1,du,ru,v,a1,d1


    '''
    2个参数
    '''
    @staticmethod
    def removeSliceFromResourceTable(s1):
        if s1 != 0:
            reser = Reservation(s1,0)
            reser.deleteSlice()
        else:
            print( 'undefined number of parameters')   

