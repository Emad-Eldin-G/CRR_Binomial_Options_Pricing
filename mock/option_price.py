import math
import random
from time import sleep

def mock_price():
    S0 = random.randrange(20, 2300)      
    vol = 10                            
    exercise = "EU"                      
    option_type = "C"                    
    K = S0 + (vol * 2.5)                 
    T = 5
    N = 30
    r = 2.8

    # base intrinsic value
    intrinsic = max(S0 - K, 0)

    # add a volatility-based premium
    premium = vol * random.uniform(0.8, 1.4)

    # discount factor (just for realism, not accurate math)
    discount = math.exp(-r/100 * T)

    # final mock price with little randomness
    price = (intrinsic + premium) * discount
    price = round(price, 2)

    compuation_time = random.uniform(0.1, 2.0)  # in seconds

    sleep(3)

    return {
        "S0": S0,
        "K": K,
        "T": T,
        "vol": vol,
        "r": r,
        "price": price,
        "exercise": exercise,
        "option_type": option_type,
        "N": N,
        "compute_time": compuation_time
    }
