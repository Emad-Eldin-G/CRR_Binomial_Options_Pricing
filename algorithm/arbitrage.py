import numpy as np

def put_call_parity(S0, K, T, r, call_price, put_price, optclass="E"):
    """
    Calculate the put-call parity.
    
    LHS = C + Ke^(-rT)
    RHS = P + S0
    """

    if optclass != "E":
        return "N/A"

    lhs = call_price + (K * np.exp(-r * T))
    rhs = put_price + S0
    return np.isclose(lhs, rhs)