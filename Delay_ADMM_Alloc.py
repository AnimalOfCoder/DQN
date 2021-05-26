import numpy as np

class Delay_ADMM_Alloc:
    def __init__(self):
        pass


    @staticmethod
    def ADMM_Alloc(V, ar, rt, Dc):
        '''
        V= percentage of resource in the base stations. use V= ones(1,B) where B is numbr of base stations
        ar is packet arrival rates of users size (1,K)
        rt is normalized achievable data rates of users in each base stations size is (K,B) k is numbr of users. 
        du is delay bound converted in seconds size (1,k)
        penalyity is represented by RO, change RO  to any value try different value
        '''

        #print('delay constrained admm running...\n')
        # this is called by the delay constrained slices for their physical resource allocation
        # Detailed explanation goes here
        #initializations
        RO = 1000 * (max(max(rt)) ** 2) #penality 
        (K,B) = np.array(rt).shape
        theta = np.zeros((K,B))
        Y = np.zeros((K,B)) 
        Z = np.zeros((K,B)) 
        zold=Z
        yold=Y
        for i in range(0, K):
            rt[i,:] = rt[i,:] * V # scale the datalink capacity according to the fraction of the base stations
        
        theta = theta+RO*(Y-Z)
        
        #iterations
        for _  in range(0, 50):
            #ms side
            pY = Y
            for i in range(0, K):   
                if (ar[0, i] / ((sum(pY[i, :] * rt[i,:]) - ar[0, i])**2)) <= 100 and sum(pY[i, :] * rt[i,:]) > ar[0, i] + 1/Dc[0,i]: # if delay less than 0.1 and when multiplied with arrival is arround 10
                    for j in range(0, B):
                        Y[i,j] =Z(i,j)-theta[i,j]/RO+(rt(i,j)/RO)*(ar[0, i]/((sum(pY[i, :] * rt[i,:]) - ar[0, i])**2))
                else:
                    for j in range(0, B):
                        Y[i,j]=Z(i,j)-theta[i,j]/RO
                max(0,Y[i,:])
                # now check if the delay is between zero and upper bound
                if (((1/(sum(Y[i,:] * rt[i,:])-ar[0, i]))>Dc[0,i]) or ((1/(sum(Y[i,:] * rt[i,:])-ar[0, i]))<0)):
                    yud=(1 / Dc[0,i]+ar[0, i]-sum(Y[i,:] * rt[i,:]))*(RO/sum(rt[i,:]**2))
                    for j in range(0, B):
                        if V[0,j]>0:
                            Y[i,j]=Y[i,j]+(yud)*(rt(i,j)/RO)
                max(0,Y[i,:])

            #bs side
            for i in range(0, B):
                if V[0,i]>0:
                    for j in range(0, K):
                        Z[j,i]=Y[j,i]+theta[j,i]/RO

                    mn=min(Z[:,i])
                    if mn<0:
                        Z[:,i]=Z[:,i]-mn
                        accessible=min(1,rt[:,i])
                        accessible=np.ceil(accessible)
                        Z[:,i]=Z[:,i] * accessible

                    if (1-sum(Z[:,i]))>=0:
                        
                        sizer= (rt[:,i]!=0).sum(0) # 求rt中i列不为0的个数，sizer=size(rt(any(rt[:,i],2),i),1)
                        abyusm=(1-sum(Z[:,i])) 
                        accessible=min(1,rt[:,i])
                        accessible=np.ceil(accessible)
                        Z[:,i]=Z[:,i]+accessible * (abyusm/sizer) 
                    else:
                        z=Z[:,i].T
                        while sum(max(0, z-min(z[np.nonzero(z)]))) > 1:
                            z = max(0,z-min(z[np.nonzero(z)]))

                        vd=sum(z[np.nonzero(z)]) - 1
                        z=z-vd / z[np.nonzero(z)].shape[0]
                        z=max(0,z)
                        Z[:,i]=z.T

            # end# if sum of y is equal to bs break loop o
            #theta update
            Fn=1
            for i in range(0, K):
                for j in range(0, B):
                    theta[i,j]=theta[i,j] + RO*(Y[i,j]-Z[i,j])

                if 1/(sum(Z[i,:] * rt[i,:]) - ar[0, i]) > Dc[0,i] or 1/(sum(Z[i,:] * rt[i,:])-ar[0, i])<0:
                    Fn=0

            if np.linalg.norm(zold-Z, ord=1)==0 and np.linalg.norm(yold-Y, ord=1)==0 and Fn==1:
                break
            else:
                zold=Z 
                yold=Y
            
            for i in range(0, K):
                Y[i,:]=Z[i,:] * V[1,:]

        return Y
