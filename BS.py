
import numpy as np
class BS:
    def __init__(self):
        pass

    '''
    updates the resouce in the base statios using the action from the DQn
    Detailed explanation goes here see resource update section of the thesis for more information
    '''
    @staticmethod
    def update_AL_pro(AL,RE,P,a):
        B = np.array(RE)[1]
        if a < 0:
            GA=sum(AL * P) # change the the allocation in the base stations to global resouce fraction view 0f the slice
            Gupdate= GA + GA * a #calculate the global updated resource fraction relative to all base statins
            v=np.zeros((1,B))
        elif a > 0:
            GA=sum(AL * P)# change the the allocation in the base stations to global resouce fraction view 0f the slice
            GR=sum(RE * P)# change the the Reservations in the base stations to global resouce fraction view 0f the slice
            Gupdate = GA + GR * a 
            v=np.zeros((1,B))
        elif a == 0: #when action is 0
            GA=sum(AL * P)# change the the allocation in the base stations to global resouce fraction view 0f the slice
            Gupdate=GA
            v=np.zeros((1,B))
        else:
            print('a must be between [-0.9:0.1:1]')
        REE = RE+AL
        xap = Gupdate / sum(REE * P)
        v = xap * REE #take the resource proportional to the reservations

        return v

