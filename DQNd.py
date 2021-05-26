
#the neural network takes the 4 paremeters(resource allocation, resouce
#utilization, QoS utility, and resource reservation )of the slice and
#outpputs an action that is a percentage is either to decrease or increase
#from the prevous allocation if action is negative and from the reserved if
#action is posetive respectively
####add path
# cs is the current state of the slice
# a is the action, r is the reward, trn is an indicator variable that tells whether to train or not. if trn is
# 1 it means the neural network is activated for training
 # if only one argument is send it will go to case1 and give action for the
 # state given in cs. if 4 artuments are sent to this function the  neural
 # network will stote all the data in replay memory. 
 # if zero argument is send this goes to case0 to initialize and congigure the neural
 # network.
class DQNd:
    def __init__(self):
        pass
    
    # create NN
    def create_NN():
        pass

    # choose the action with max Q value
    def choose_action():
        pass

    # register tuple in a memoryd and trian
    def store_transition():
        pass