# Cox, Ross and Rubinstein Binomial Method for Options Pricing using Backward Induction
> European and American Put/Call Option pricing.


- Streamlit Dashboard 🟢
- Python Dynamic Programming 🟠
- NumPy Vectorization 🔴
- C++ Dynamic Programming 🔴
- Binomial Tree Visualizer 🔴
  
## How to run project
### 1. Setup Environment 
- go to main directory 
```bash
cd <name_of_cloned_to_directory>/
```
- create python virtual environment
```bash
python -m venv venv
```
> Done once
- activate virtual environemnt
```bash
source venv/bin/activate
```
> Whenever you restart your IDE or Terminal, you will need to reactivate the virtual environemnt,
> but all the requirements will be there so no need to reinstall
- install requirements
```bash
pip install -r requirements.txt
```
> Done once

### 2. Run Project
- To run main Streamlit Project
```bash
streamlit run main.py
```  

<br>

## CRR Binomial Method (Cox-Ross-Rubinstein)

The CRR binomial model prices options by assuming the underlying asset can move **up** or **down** at each step. Under the **risk-neutral measure**, the discounted expected payoff must equal today’s price. This leads to simple recursive pricing at each step of the binomial tree.

### One-step pricing

```math
C_{0} = e^{-rT} \, E^{*}(C_{T})
      = e^{-rT} \big( p\,C_{u} + (1 - p)\,C_{d} \big)
```

### N-step pricing (closed form)

```math
C_{0} = e^{-rT} \sum_{k=0}^{N}
        \binom{N}{k} \, (p^{*})^{k} (1 - p^{*})^{N-k}\,
        C\!\big(S_{0} u^{k} d^{\,N-k}\big)
```

---

## Difference Between Calls and Puts

| Option Type | Payoff at Maturity | Interpretation                      |
| ----------- | ------------------ | ----------------------------------- |
| **Call**    | `max(S_T - K, 0)`  | Right to buy the asset at strike K  |
| **Put**     | `max(K - S_T, 0)`  | Right to sell the asset at strike K |

Both are priced using the same binomial formulas; only the payoff function changes.

---

## European vs American Options

| Feature     | European              | American                       |
| ----------- | --------------------- | ------------------------------ |
| Exercisable | Only at maturity      | Anytime up to maturity         |
| Pricing     | Closed-form CRR works | Must check for early exercise  |
| Complexity  | Easier                | More computationally intensive |
| Example     | Index options         | Most equity options            |

In the binomial tree:

* **European:** only use discounted expected value at each node.
* **American:** at each node compare:
  continuation value **vs** immediate exercise payoff,
  and take the **maximum**.
