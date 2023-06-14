import numpy as np 
import pandas as pd 

def film_loss(aim, weight, observation, average=False, debug=False, betterfgood=True):
    # Calculate film loss 
    
    loss_absorbation   = np.mean(weight['Absorption'] * (abs(aim['Absorption'] - observation[0])))
    loss_transimission = np.mean(weight['Transmission'] * (abs(aim['Transmission'] - observation[1])))
    loss_refraction    = np.mean(weight['Reflection'] * (abs(aim['Reflection'] - observation[2])))


    # 检查薄膜状态
    if debug:
        print(f'Postoptimisation state: [Absorption]{np.mean(observation[0])}, [Transmission]{np.mean(observation[1])}, [Reflection]{np.mean(observation[2])}')
        print(f"Ideal state: [Absorption]{np.mean(aim['Absorption'])}, [Transmission]{np.mean(aim['Transmission'])}, [Reflection]{np.mean(aim['Reflection'])}")
        print(f"film_loss: {np.sum([loss_absorbation, loss_transimission, loss_refraction])}")
        print(f"observation: {1 / np.sum([loss_absorbation, loss_transimission, loss_refraction])}")
        
    if average:
        if betterfgood:
        #print(np.sum([loss_absorbation, loss_transimission, loss_refraction]))
            return 1 / np.sum([loss_absorbation, loss_transimission, loss_refraction])
        else:
            return np.sum([loss_absorbation, loss_transimission, loss_refraction])
    else:
        return loss_absorbation, loss_transimission, loss_refraction

