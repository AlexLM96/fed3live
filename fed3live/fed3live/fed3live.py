"""
This is the main module for analysis of the bandit task.
"""

import os
import sys
import pandas as pd
import datetime
import numpy as np
import statsmodels.api as sm
import pkg_resources

#%%

def load_sampledata():
    """Loads sample data from a bandit task that has the specification
    shared in Arduino example
    
    Parameters
    ----------

    Returns
    --------
    samle_data : pd.DataFrame
        Sample data
    """

    filename = pkg_resources.resource_filename(__name__, 'sample_data.csv')
    sample_data = pd.read_csv(filename)
    return sample_data

def filter_data(data_choices):
    """Filters the data to only show pokes "Left" or "Right" events, which are pokes that did not occur 
    during time out, or during pellet dispensing.
    
    Parameters
    ----------
    data_choices : pandas.DataFrame
        The fed3 data file

    Returns
    --------
    filtered_data : pd.DataFrame
        Filtered fed3 data file
    """
    try:
        filtered_data = data_choices[np.logical_and.reduce((data_choices["Event"]!="Pellet",
                                                                data_choices["Event"]!="LeftinTimeOut",
                                                                data_choices["Event"]!="RightinTimeout",
                                                                data_choices["Event"]!="LeftDuringDispense",
                                                                data_choices["Event"]!="RightDuringDispense",
                                                                data_choices["Event"]!="LeftShort",
                                                                data_choices["Event"]!="RightShort"))]
    except:
        filtered_data = data_choices[np.logical_and.reduce((data_choices["fed3EventActive"]!="Pellet",
                                                                data_choices["fed3EventActive"]!="LeftinTimeOut",
                                                                data_choices["fed3EventActive"]!="RightinTimeout",
                                                                data_choices["fed3EventActive"]!="LeftDuringDispense",
                                                                data_choices["fed3EventActive"]!="RightDuringDispense",
                                                                data_choices["fed3EventActive"]!="LeftShort",
                                                                data_choices["fed3EventActive"]!="RightShort"))]
    
    filtered_data.iloc[:,0] = pd.to_datetime(filtered_data.iloc[:,0])
    
    return filtered_data

def binned_paction(data_choices, window=5):
    """Bins actions from fed3 bandit file
    
    Parameters
    ----------
    data_choices : pandas.DataFrame
        The fed3 data file
    window : int
        Sliding window by which the probability of choosing left will be calculated

    Returns
    --------
    p_left : pandas.Series
        Probability of choosing left. Returns pandas.Series of length data_choices.shape[0] - window
    
    """
    f_data_choices = filter_data(data_choices)
    actions = f_data_choices["Event"]
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

def count_pellets(data_choices):
    """Counts the number of pellets in fed3 data file
    
    Parameters
    ----------
    data_choices : pandas.DataFrame
        The fed3 data file

    Returns
    --------
    c_pellets : int
        total number of pellets
    """

    f_data_choices = filter_data(data_choices)
    try:
        block_pellet_count = f_data_choices["fed3BlockPelletCount"]
    except:
        block_pellet_count = f_data_choices["Block_Pellet_Count"]
      
    c_diff = np.diff(block_pellet_count)
    c_diff2 = np.where(c_diff < 0, 1, c_diff)
    c_pellets = int(c_diff2.sum())
    
    return c_pellets

def count_pokes(data_choices):
    """Counts the number ofpokes in fed3 data file
    
    Parameters
    ----------
    data_choices : pandas.DataFrame
        The fed3 data file
        
    Returns
    --------
    all_pokes : int
        total number of pellets
    """
    
    f_data_choices = filter_data(data_choices)
    try:
        left_count = f_data_choices["fed3LeftCount"]
        right_count = f_data_choices["fed3RightCount"]
    except:
        left_count = f_data_choices["Left_Poke_Count"]
        right_count = f_data_choices["Right_Poke_Count"]
    

    c_left_diff = np.diff(left_count)
    c_left_diff2 = np.where(np.logical_or(c_left_diff < 0, c_left_diff > 1), 1, c_left_diff)
    
    c_right_diff = np.diff(right_count)
    c_right_diff2 = np.where(np.logical_or(c_right_diff < 0, c_right_diff > 1), 1, c_right_diff)
    
    all_pokes = c_left_diff2.sum() + c_right_diff2.sum()

    return all_pokes

def pokes_per_pellet(data_choices):
    """Calculates pokes per pellets from fed3 bandit file
    
    Parameters
    ----------
    data_choices : pandas.DataFrame
        The fed3 data file

    Returns
    --------
    ppp : int
        pokes per pellets
    """

    f_data_choices = filter_data(data_choices)
    pellets = count_pellets(f_data_choices)
    pokes = count_pokes(f_data_choices)
    
    if (pellets == 0) | (pokes == 0):
        ppp = np.nan
    else:
        ppp = pokes/pellets
    
    return ppp

def poke_accuracy(data_choices, return_avg=False):
    """Calculates pokes per pellets from fed3 bandit file
    
    Parameters
    ----------
    data_choices : pandas.DataFrame
        The fed3 data file
    return_avg : bool
        If True, returns the average accuracy of data_choices. If False, returns np.array of bool of 

    Returns
    --------
    ppp : int
        pokes per pellets
    """

    f_data_choices = filter_data(data_choices)
    try:
        events = f_data_choices["Event"]
        prob_left = f_data_choices["Session_type"]
        prob_right = f_data_choices["Device_Number"]
    except:
        events = f_data_choices["fed3EventActive"]
        prob_left = f_data_choices["fed3SessionType"]
        prob_right = f_data_choices["fed3DeviceNumber"]

    high_pokes = np.logical_or(np.logical_and(events == "Left", prob_left > prob_right), 
                               np.logical_and(events == "Right", prob_left < prob_right))
    high_pokes = np.where(prob_left == prob_right, np.nan, high_pokes)
    
    if return_avg:
        return high_pokes.mean()
    else:
        return high_pokes

def reversal_peh(data_choices, min_max, return_avg = False):
    """Calculates the probability of poking in the high probability port around contingency switches
    from fed3 data file
    
    Parameters
    ----------
    data_choices : pandas.DataFrame
        The fed3 data file
    min_max : tuple
        Event window around the switches to analyze. E.g. min_max = (-10,11) will use a time window
        of 10 events before the switch to 10 events after the switch.
    return_avg : bool
        If True, returns only the average trace. If False, returns all the trials.

    Returns
    --------
    c_days : int
        days in data file
    c_pellets : int
        total number of pellets
    c_ppd : int
        average pellets per day
    
    """
    f_data_choices = filter_data(data_choices)
    try:
        device_number = f_data_choices["fed3DeviceNumber"]
        event = f_data_choices["fed3EventActive"]
    except:
        device_number = f_data_choices["Device_Number"]
        event = f_data_choices["Event"]
    
    switches = np.where(np.diff(device_number) != 0)[0] + 1
    switches = switches[np.logical_and(switches+min_max[0] > 0, switches+min_max[1] < data_choices.shape[0])]

    all_trials = []
    for switch in switches:
        c_trial = np.zeros(np.abs(min_max[0])+min_max[1])
        counter = 0
        for i in range(min_max[0],min_max[1]):
            c_choice = event.iloc[switch+i]
            c_prob_right = device_number.iloc[switch+i]
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
    
def win_stay(data_choices):
    """Calculates the win-stay probaility
    
    Parameters
    ----------
    data_choices : pandas.DataFrame
        The fed3 data file

    Returns
    --------
    win_stay_p : int
        win-stay probability
    """
    f_data_choices = filter_data(data_choices)
    try:
        block_pellet_count = f_data_choices["fed3BlockPelletCount"]
        events = f_data_choices["fed3EventActive"]
    except:
        block_pellet_count = f_data_choices["Block_Pellet_Count"]
        events = f_data_choices["Event"]
        
    win_stay = 0
    win_shift = 0
    for i in range(f_data_choices.shape[0]-1):
        c_choice = events.iloc[i]
        next_choice = events.iloc[i+1]
        c_count = block_pellet_count.iloc[i]
        next_count = block_pellet_count.iloc[i+1]
        if np.logical_or(next_count-c_count == 1, next_count-c_count < 0):
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
                
    if (win_stay+win_shift) == 0:
        win_stay_p = np.nan
    else:
        win_stay_p = win_stay / (win_stay + win_shift)
    
    return win_stay_p

def lose_shift(data_choices):
    """Calculates the lose-shift probaility
    
    Parameters
    ----------
    data_choices : pandas.DataFrame
        The fed3 data file

    Returns
    --------
    lose_shift_p : int
        lose-shift probability
    """
    f_data_choices = filter_data(data_choices)
    try:
        block_pellet_count = f_data_choices["fed3BlockPelletCount"]
        events = f_data_choices["fed3EventActive"]
    except:
        block_pellet_count = f_data_choices["Block_Pellet_Count"]
        events = f_data_choices["Event"]
    
    lose_stay = 0
    lose_shift = 0
    for i in range(f_data_choices.shape[0]-1):
        c_choice = events.iloc[i]
        next_choice = events.iloc[i+1]
        c_count = block_pellet_count.iloc[i]
        next_count = block_pellet_count.iloc[i+1]
        if np.logical_or(next_count-c_count == 1, next_count-c_count == -19):
            c_outcome = 1
        else:
            c_outcome = 0
            
        if c_outcome == 0:
            if ((c_choice == "Left") and (next_choice == "Left")):
                lose_stay += 1
            elif ((c_choice == "Right") and (next_choice == "Right")):
                lose_stay += 1
            elif((c_choice == "Left") and (next_choice == "Right")):
                lose_shift += 1
            elif((c_choice == "Right") and (next_choice == "Left")):
                lose_shift += 1
                 
    if (lose_shift+lose_stay) == 0:
        lose_shift_p = np.nan
    else:
        lose_shift_p = lose_shift / (lose_shift + lose_stay)
    
    return lose_shift_p

def side_prewards(data_choices):
    """Returns whether the relationship
    
    Parameters
    ----------
    data_choices : pandas.DataFrame
        The fed3 data file
        
    Returns
    --------
    left_reward : int
        win-stay probability
    right_reward : int
        lose-shift probability
    """
    f_data_choices = filter_data(data_choices)
    try:
        block_pellet_count = f_data_choices["fed3BlockPelletCount"]
        events = f_data_choices["fed3EventActive"]
    except:
        block_pellet_count = f_data_choices["Block_Pellet_Count"]
        events = f_data_choices["Event"]
    
    left_reward = []
    right_reward = []
    for i in range(f_data_choices.shape[0]-1):
        c_event = events.iloc[i]
        c_count = block_pellet_count.iloc[i]
        next_count = block_pellet_count.iloc[i+1]
        if c_event == "Left":
            right_reward.append(0)
            if (next_count-c_count) != 0:
                left_reward.append(1)
            else:
                left_reward.append(0)
        
        elif c_event == "Right":
            left_reward.append(0)
            if (next_count-c_count) != 0:
                right_reward.append(1)
            else:
                right_reward.append(0)
                
    return left_reward, right_reward

def side_nrewards(data_choices):
    """Returns whether the relationship
    
    Parameters
    ----------
    data_choices : pandas.DataFrame
        The fed3 data file
        
    Returns
    --------
    left_reward : int
        win-stay probability
    right_reward : int
        lose-shift probability
    """
    f_data_choices = filter_data(data_choices)
    try:
        block_pellet_count = f_data_choices["fed3BlockPelletCount"]
        events = f_data_choices["fed3EventActive"]
    except:
        block_pellet_count = f_data_choices["Block_Pellet_Count"]
        events = f_data_choices["Event"]
    
    left_nreward = []
    right_nreward = []
    for i in range(f_data_choices.shape[0]-1):
        c_event = events.iloc[i]
        c_count = block_pellet_count.iloc[i]
        next_count = block_pellet_count.iloc[i+1]
        if c_event == "Left":
            right_nreward.append(0)
            if (next_count - c_count) != 0:
                left_nreward.append(0)
            else:
                left_nreward.append(1)
        
        elif c_event == "Right":
            left_nreward.append(0)
            if (next_count - c_count) != 0:
                right_nreward.append(0)
            else:
                right_nreward.append(1)
                
    return left_nreward, right_nreward

def create_X(data_choices, left_reward, right_reward, n_feats):
    """Creates matrix of choice and previouse interaction of choice*reward based on the
    output of the side_rewards function.
    
    Parameters
    ----------
    data_choices : pandas.DataFrame
        The fed3 data file
    left_reward : array-like
        First output of side_rewards
    right_reward : array-like
        Second output of side_rewards
    n_feats : int
        Number of trials in past to be analyzed
        
    Returns
    --------
    X_df : pandas.DataFrame
        Matrix with choice and interaction of choice*trial for the past n_feats trials
    """
    f_data_choices = filter_data(data_choices)
    try:
        events = f_data_choices["fed3EventActive"]
    except:
        events = f_data_choices["Event"]
    
    reward_diff = np.subtract(left_reward,right_reward)
    X_dict = {}
    for i in range(data_choices.shape[0]-n_feats):
        c_idx = i + n_feats
        X_dict[c_idx+1] = [events.iloc[c_idx]]
        for j in range(n_feats):
            X_dict[c_idx+1].append(reward_diff[c_idx-(j+1)])
            
    X_df = pd.DataFrame(X_dict).T
    col_names = ["Choice"]
    for i in range(n_feats):
        col_names.append("Reward diff_t-" + str(i+1))
    
    X_df.columns = col_names
    
    return X_df

def logit_regr(X_df):
    """Fits a statsmodels logistic regression based on the output of create_X and returns the regression oject
    
    Parameters
    ----------
    X_df : pd.DataFrame
        Output of create_X function

    Returns
    --------
    c_regr : statsmodels.regression
        statsmodel logistic regression object, see https://www.statsmodels.org/dev/generated/statsmodels.discrete.discrete_model.Logit.html
    """
    c_X = X_df.iloc[:,1:].astype(int).to_numpy()
    c_y = [1 if choice == "Left" else 0 for choice in X_df["Choice"]]
   
    c_regr =sm.Logit(c_y, c_X).fit()
    
    return c_regr

