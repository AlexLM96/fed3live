# -*- coding: utf-8 -*-
"""
Created on Fri Feb  3 14:11:01 2023

@author: Alex
"""

import pandas as pd
import datetime
import numpy as np
import statsmodels.api as sm

#%%

def pellets_per_day(data_choices):
    c_diff = np.diff(data_choices["fed3BlockPelletCount"])
    c_diff2 = np.where(c_diff < 0, 1, c_diff)
    c_pellets = int(c_diff2.sum())
    
    c_start = data_choices["fed3Time"].iloc[0].date()
    c_end = data_choices["fed3Time"].iloc[-1].date()
    c_days = (c_end-c_start).days
    
    c_ppd = c_pellets/c_days
    
    return c_days, c_pellets, c_ppd

def binned_paction(actions, window):
    p_left = []
    for i in range(len(actions)-window):
        c_slice = actions[i:i+window]
        n_left = 0
        for action in c_slice:
            if action == "Left":
                n_left += 1
            
        c_p_left = n_left / window
        p_left.append(c_p_left)
        
    return p_left

def reversal_peh(data_choices, min_max, return_avg = False):
    switches = np.where(np.diff(data_choices["fed3DeviceNumber"]) != 0)[0] + 1
    switches = switches[np.logical_and(switches+min_max[0] > 0, switches+min_max[1] < data_choices.shape[0])]
    #print(switches)
    all_trials = []
    for switch in switches:
        c_trial = np.zeros(np.abs(min_max[0])+min_max[1])
        counter = 0
        for i in range(min_max[0],min_max[1]):
            c_choice = data_choices["fed3EventActive"].iloc[switch+i]
            c_prob_right = data_choices["fed3DeviceNumber"].iloc[switch+i]
            if c_prob_right < 50:
                c_high = "Left"
            elif c_prob_right > 50:
                c_high = "Right"
            else:
                print("Error")
                
            if c_choice == c_high:
                c_trial[counter] += 1
                
            counter += 1
        
        all_trials.append(c_trial)

    aall_trials = np.vstack(all_trials)
    
    if return_avg:
        avg_trial = aall_trials.mean(axis=0)
        return avg_trial
        
    else:
        return aall_trials
    
def win_lose_action(data_choices):
    win_stay = 0
    win_shift = 0
    lose_stay = 0
    lose_shift = 0
    for i in range(data_choices.shape[0]-1):
        c_choice = data_choices["fed3EventActive"].iloc[i]
        next_choice = data_choices["fed3EventActive"].iloc[i+1]
        c_count = data_choices["fed3BlockPelletCount"].iloc[i]
        next_count = data_choices["fed3BlockPelletCount"].iloc[i+1]
        if np.logical_or(next_count-c_count == 1, next_count-c_count == -19):
            c_outcome = 1
        else:
            c_outcome = 0
            
        if c_outcome == 1:
            if ((c_choice == "Left") and (next_choice == "Left")):
                win_stay += 1
            elif ((c_choice == "Right") and (next_choice == "Right")):
                win_stay += 1
            elif((c_choice == "Left") and (next_choice == "Right")):
                win_shift += 1
            elif((c_choice == "Right") and (next_choice == "Left")):
                win_shift += 1
                
        elif c_outcome == 0:
            if ((c_choice == "Left") and (next_choice == "Left")):
                lose_stay += 1
            elif ((c_choice == "Right") and (next_choice == "Right")):
                lose_stay += 1
            elif((c_choice == "Left") and (next_choice == "Right")):
                lose_shift += 1
            elif((c_choice == "Right") and (next_choice == "Left")):
                lose_shift += 1
                
    win_stay_p = win_stay / (win_stay + win_shift)
    lose_shift_p = lose_shift / (lose_shift + lose_stay)
    
    return win_stay_p, lose_shift_p

def side_rewards(data_choices):
    left_reward = []
    right_reward = []
    for i in range(data_choices.shape[0]-1):
        c_event = data_choices.iloc[i,:]
        c_count = c_event["fed3BlockPelletCount"]
        next_count = data_choices["fed3BlockPelletCount"].iloc[i+1]
        if c_event["fed3EventActive"] == "Left":
            right_reward.append(0)
            if np.logical_or(next_count - c_count == 1, next_count - c_count == -19):
                left_reward.append(1)
            else:
                left_reward.append(0)
        
        elif c_event["fed3EventActive"] == "Right":
            left_reward.append(0)
            if np.logical_or(next_count - c_count == 1, next_count - c_count == -19):
                right_reward.append(1)
            else:
                right_reward.append(0)
                
    return left_reward, right_reward

def create_X(data_choices, left_reward, right_reward, n_feats):
    reward_diff = np.subtract(left_reward,right_reward)
    X_dict = {}
    for i in range(data_choices.shape[0]-n_feats):
        c_idx = i + n_feats
        X_dict[c_idx+1] = [data_choices["fed3EventActive"].iloc[c_idx]]
        for j in range(n_feats):
            X_dict[c_idx+1].append(reward_diff[c_idx-(j+1)])
            
    X_df = pd.DataFrame(X_dict).T
    col_names = ["Choice"]
    for i in range(10):
        col_names.append("Reward diff_t-" + str(i+1))
    
    X_df.columns = col_names
    
    return X_df

def logit_regr(X_df):
     c_X = X_df.iloc[:,1:].astype(int).to_numpy()
     c_y = [1 if choice == "Left" else 0 for choice in X_df["Choice"]]
    
     c_regr =sm.Logit(c_y, c_X).fit()
     
     return c_regr
 

def pokes_per_pellet(data_choices):
    c_diff = np.diff(data_choices["fed3BlockPelletCount"])
    c_diff2 = np.where(c_diff < 0, 1, c_diff)
    c_pellets = int(c_diff2.sum())
    
    c_left_diff = np.diff(data_choices["fed3LeftCount"])
    c_left_diff2 = np.where(np.logical_or(c_left_diff < 0, c_left_diff > 1), 1, c_left_diff)
    
    c_right_diff = np.diff(data_choices["fed3RightCount"])
    c_right_diff2 = np.where(np.logical_or(c_right_diff < 0, c_right_diff > 1), 1, c_right_diff)
    
    all_pokes = c_left_diff2.sum() + c_right_diff2.sum()
    ppp = all_pokes/c_pellets
    
    return ppp