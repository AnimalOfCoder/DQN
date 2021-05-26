import numpy as np

C_min_km = 100
t_max_km = 100
LAMBDA_km = 80

class ResourceReservation():
    def __init__(self, n, m, action, k):
        self.k = k # the number of users
        self.m = 2 # the mumber of slices
        self.n = 4 # the number of BSs
        self.V = np.zeros(m, n) # BS allocated resource matrix
        self.V_ = np.zeros(self.m, self.n)
        self.F_ = np.zeros(n)
        self.T = 0

        self.C_min = np.zeros(k * m * n)

        self.I_user = np.zeros(k * m * n)

        self.C = np.zeros(k * m * n) # slice m, BS n; the average achievable data rate of the user k_m from BS n

        self.r_min_k = np.zeros(m)  # minimum rate requirement of the user on slice m; (delay constrained user, rate constrained user)

        self.I_BS = np.zeros(m * n) # minimum resource requirements of the slice m to other slices on a specific BS n

        self.E = np.zeros(m * n) # The reserved resource for a slice m, on BS n

        self.F = np.ones(n) # total amount of unused resource at BS n

        self.I_slice = np.zeros(m * n)

        self.v_m = np.zeros(m) # the overall resource allocation of the slice

        self.e_m = np.zeros(m) # the overall resource reservation of the slice

        self.action = action
        
        # calculate C 
        self.calculateC()
        # calculate I_user
        self.calculateI_user()
        # calculate C_min
        self.calculateC_min()

        self.calculatev_m()
        self.calculatee_m()

    # todo, 信息增益没有 by (1)
    def calculateC():
        return ''

    # todo (12)
    def calculateI_user():
        return ''

    def calculateC_min():
        for k in range(self.k):
            for m in range(self.m):
                for n in range(self.n):
                    self.C_min[k,m,n] = self.I_user[k,m,n] * self.getMinRate(k)

    def getMinRate(k):
        # delay user = rate user
        if self.k % 2 == 0:
            return C_min_km
        else:
            return LAMBDA_km + 1 / t_max_km

    def calculateI_slice():
        slices = np.sum(C_min, axis=0)
        for m in range(self.m):
            for n in range(self.n):
            self.I_slice[m,n] = slices[m, n] / sum(slices[m])
     
    def calculatev_m():
        for m in range(self.m):
            total = 0
            for n in range(self.n):
                total += self.I_slice[m, n] * self.V[m, n]

            self.v_m[m] = total

    def calculatee_m():
        for m in range(self.m):
            total = 0
            for n in range(self.n):
                total += self.I_slice[m, n] * self.E[m, n]

            self.e_m[m] = total

    def calculateI_BS():
        slices = np.sum(C_min, axis=0)
        for m in range(self.m):
            for n in range(self.n):
            self.I_BS[m,n] = slices[m, n] / sum(slices)

    def calculateE():
        for m in range(self.m):
            for n in range(self.n):
                E[m,n] = F[n] * self.I_BS[m, n]

    def updateV():
        for m in range(m):
            for n in range(n):
                if self.action[m] > 0:
                    x = (self.v_m(m) + self.action[m] * self.e_m[m]) / (self.v_m[m] + self.e_m[m])
                else:
                    x = (self.action[m] + 1) * self.v_m(m) / (self.v_m[m] + self.e_m[m])

                self.V_[m,n] = x * self.V[m, n]

        return self.V_

    def updateF():
        diff = np.sum(self.V_ - self.V)
        for n in range(n):
            self.F_[n] = self.F[n] - diff[n]

        return self.F_           

    def run():
        '''
        Calculate the weights I_slice of BSs to each slice by (16)
        '''
        self.calculateI_slice()

        if self.T == 0:
            '''
            Collect the minimum resource requirements of each
            user of the slice by (13) and sum up them to find the
            minimum requirement of the slice;
            '''
            # self.calculateC_min()
            '''
            Calculate the reservation weight I_BS by (14) and the m,n 
            initial slice resource reservation Em,n by (15);
            ''' 
            self.calculateI_BS()

            self.calculateE()

        else:
            '''
            Collect the updated resource allocation V-m,n from all slices by (23);
            '''
            self.V = self.updateV()
        
        '''
        Update the unused resource Fn on each BS by (24);
        '''
            self.F = self.updateF()


        if(self.traffic_statistics_changed): # todo, unknow variable
            '''
            Update the reservation weight I_BS by (14) and I_slice by (16)
            Update the slice resource reservation Em,n by (15)
            '''
            self.calculateI_BS()
            self.calculateI_slice()
            self.calculateE()

        self.T = self.T + 1

        return self.v_m, self.e_m







    



