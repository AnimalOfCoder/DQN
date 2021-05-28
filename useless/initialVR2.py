from Reservation import Reservation
import numpy as np

class initialVR2:

    def __init__(self, rtV, Q, rtV2, Q2):
        # self.rtV = rtV
        # self.Q = Q
        # self.rtV2 = rtV2
        # self.Q2 = Q2
        pass

    '''
        # this functions accepts the achievable data rate of the users of the slices 
        # and their QoS and find which users are feasible for the available
        # resource. 
        # removes some users if not feasible. 
        # the feasiblility is checked using SINR based admission control. start accepting the users with higher
        # SINR.user is addmited in this case does not mean the users must have resource allocation from that base station only, it is used only for checking if
        # the resource is enouph for all users.
        # rtV is the normalized achievable data rate of the users of slice 1
        # rtv2.............................................................2
        # Q minimum resource requirement of the users of slice1
        # Q2..................................................2
        # V and V2 are not used in this code, used in my previous design
        # accept is a vector showing whether the vector of users  of slice 1are accepted or
        # not. 
        # if a user is accepted its corresponding value in accept will be 1.
        # if a user is rejected its corresponding value will be 0 in the accept
        # vector.
        # accept2 ...... for slice 2
        # res is ID given to slice 1 if at least one user is accepted. the ID is
        # stored in the memory(store.m). the resource update and reservation
        # request of the slice will be identified by this ID
        # res2 is ID for slice2.
    '''
    
    def initial_VR2(rtV, Q, rtV2, Q2):
        print('filtering feasiblity of user demands, removes if not feasible...\n')
        #initial virtual resource allocation of the slice in the base stations
        _, un = Reservation.getUnusedResourceAndNumOfSlices()
        [K,B]=np.array(rtV).shape
        [K2,B2]=np.array(rtV2).shape
        qyu=np.zeros((K,B))
        for i in range(0, K):
            for j in range(0, B):
                qyu[i,j]=Q[0,i]/rtV[i,j]# how much fractions is required by the users in each bs assuming single user base station associations
        
        qyu2=np.zeros((K2,B2))
        for i in range(0, K2):
            for j in range(0, B2):
                qyu2[i,j]=Q2[0,i]/rtV2[i,j]# how much fractions is required by the users in each bs assuming single user base station associations

        #calculate the resource requitement of the slice in the BSs assumig every user is admitted sequencially as they come to the nearest BS
        VR=np.zeros((1,B))
        VR2=np.zeros((1,B2))
        accepF=np.zeros((1,K))#how much percent of the user is accepted
        copyr=rtV
        accepF2=np.zeros((1,K2))#how much percent of the user is accepted
        copyr2=rtV2
        wh=0
        while wh <= K*B+K2*B2:
            maxr1=copyr.max()# the smallest user bs distance combination
            maxr2=copyr2.max()# the smallest user bs distance combination    for i=1:1:K
            if maxr1>maxr2:
                maxr=maxr1
                for i in range(0, K):
                    for m in range(0, B):
                        if copyr[i,m]==maxr and (accepF[0,i]+1)!=2: # plus one is used to ignore very small fraction
                            if un[0,m] >= qyu[i,m]*(1-accepF[0,i]) and qyu[i,m]>0 and un[0,m]>0:
                                VR[0,m]=VR[0,m]+qyu[i,m]*(1-accepF[0,i])
                                un[0,m]=un[0,m]-qyu[i,m]*(1-accepF[0,i])
                                accepF[0,i]=1
                            elif un[0,m]<qyu[i,m]*(1-accepF[0,i]) and  qyu[i,m]>0 and un[0,m]>0:
                                VR[0,m]=VR[0,m]+un[0,m]
                                un[0,m]=0
                                accepF[0,i]=accepF[0,i]+un[0,m]/(qyu[i,m]*(1-accepF[0,i]))
                            
                            copyr[i,m]=0
            else:
                maxr=maxr2
                for i in range(0, K2):
                    for m in range(0, B2):
                        if copyr2[i,m]==maxr and (accepF2[0,i]+1)!=2: # plus one is used to ignore very small fraction
                            if un[0,m]>=qyu2[i,m]*(1-accepF2[0,i]) and qyu2[i,m]>0 and un[0,m]>0:
                                VR2[0,m]=VR2[0,m]+qyu2[i,m]*(1-accepF2[0,i])
                                un[0,m]=un[0,m]-qyu2[i,m]*(1-accepF2[0,i])
                                accepF2[0,i]=1
                            elif un[0,m]<qyu2[i,m]*(1-accepF2[0,i]) and  qyu2[i,m]>0 and un[0,m]>0:
                                VR2[0,m]=VR2[0,m]+un[0,m]
                                un[0,m]=0
                                accepF2[0,i]=accepF2[0,i]+un[0,m]/(qyu2[i,m]*(1-accepF2[0,i]))
                            copyr2[i,m]=0


            if (copyr.max()==0 and copyr2.max()==0) or (accepF.min()==1 and accepF2.min()==1):
                break

            wh=wh+1


        accept=np.floor(accepF)
        accept2=np.floor(accepF2)
        if np.sum(accept) >= 1: # check if there is at leasst one user fully accepted
            S, _ = Reservation.getUnusedResourceAndNumOfSlices()
            res=S+1
            V=VR
            RQ=np.zeros((1,B))
            Reservation(res,np.zeros((1,B)),RQ).initialization()
        else:
            res=0 # reject the slice. no enouph resource
            V=np.zeros((1,B))

        if np.sum(accept2)>=1: # check if there is at leasst one user fully accepted
            S, _ = Reservation.getUnusedResourceAndNumOfSlices()
            res2=S+1
            V2=VR2
            RQ2=np.zeros((1,B))
            Reservation(res2,np.zeros((1,B)),RQ2).initialization()
        else:
            res2=0 # reject the slice. no enouph resource
            V2=np.zeros((1,B))

        
        return res, V, accept, res2, V2, accept2
 
