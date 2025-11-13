"""
Let's carefully work through the payoff calculations step by step.
"""

def analyze_clairvoyance_payoffs():
    """Analyze each scenario in the Clairvoyance Game."""
    
    P = 1.0  # pot size
    B = 1.0  # bet size
    
    print("CLAIRVOYANCE GAME PAYOFF ANALYSIS")
    print("=" * 50)
    print(f"Initial pot size: {P}")
    print(f"Bet size: {B}")
    print("Y knows both hands. Y's hand beats X 50% of the time.")
    print()
    
    scenarios = [
        ("Check Always", "Y always checks regardless of hand strength"),
        ("Bet Nuts Only", "Y bets only when holding winning hand (50% of time)"),
        ("Bluff Only", "Y bets only when holding losing hand (50% of time)"), 
        ("Bet Always", "Y bets regardless of hand strength")
    ]
    
    for y_strategy, description in scenarios:
        print(f"Y Strategy: {y_strategy}")
        print(f"Description: {description}")
        print()
        
        if y_strategy == "Check Always":
            # Always go to showdown
            x_fold_ev = 0.5 * P - 0.5 * P  # Win 50%, lose 50%
            x_call_ev = 0.5 * P - 0.5 * P  # Same as fold since no betting
            print(f"  X Fold EV: {x_fold_ev}")
            print(f"  X Call EV: {x_call_ev}")
            
        elif y_strategy == "Bet Nuts Only":
            # Y bets 50% of time (when Y has nuts), checks 50% of time (when Y has bluff)
            # When Y checks (has bluff): X wins at showdown
            # When Y bets (has nuts): X must decide fold vs call
            
            # If X always folds:
            fold_when_y_checks = P  # X wins pot at showdown (Y has bluff)
            fold_when_y_bets = -P   # X folds, loses pot
            x_fold_ev = 0.5 * fold_when_y_checks + 0.5 * fold_when_y_bets
            
            # If X always calls:
            call_when_y_checks = P  # X wins pot at showdown (Y has bluff)  
            call_when_y_bets = -(P + B)  # X calls and loses to nuts
            x_call_ev = 0.5 * call_when_y_checks + 0.5 * call_when_y_bets
            
            print(f"  X Fold EV: {x_fold_ev}")  
            print(f"  X Call EV: {x_call_ev}")
            
        elif y_strategy == "Bluff Only":
            # Y bets 50% of time (when Y has bluff), checks 50% of time (when Y has nuts)
            # When Y checks (has nuts): X loses at showdown
            # When Y bets (has bluff): X must decide fold vs call
            
            # If X always folds:
            fold_when_y_checks = -P  # X loses pot at showdown (Y has nuts)
            fold_when_y_bets = -P    # X folds, loses pot  
            x_fold_ev = 0.5 * fold_when_y_checks + 0.5 * fold_when_y_bets
            
            # If X always calls:
            call_when_y_checks = -P  # X loses pot at showdown (Y has nuts)
            call_when_y_bets = P + B # X calls and wins vs bluff
            x_call_ev = 0.5 * call_when_y_checks + 0.5 * call_when_y_bets
            
            print(f"  X Fold EV: {x_fold_ev}")
            print(f"  X Call EV: {x_call_ev}")
            
        elif y_strategy == "Bet Always":
            # Y always bets regardless of hand strength
            # X must decide fold vs call, knowing Y bets with both nuts and bluffs
            
            # If X always folds:
            x_fold_ev = -P  # Always lose the pot
            
            # If X always calls:  
            call_vs_nuts = -(P + B)  # Call and lose to nuts (50% of time)
            call_vs_bluff = P + B    # Call and win vs bluff (50% of time)
            x_call_ev = 0.5 * call_vs_nuts + 0.5 * call_vs_bluff
            
            print(f"  X Fold EV: {x_fold_ev}")
            print(f"  X Call EV: {x_call_ev}")
            
        print()
    
    # Now create the payoff matrix
    print("PAYOFF MATRIX (X's perspective)")
    print("Rows: [Fold, Call], Cols: [Check Always, Bet Nuts Only, Bluff Only, Bet Always]")
    
    payoff = [
        [0, 0, -P, -P],           # X Fold vs [Check, Bet Nuts, Bluff, Bet All]
        [0, -(P+B)/2, (P+B)/2, 0]  # X Call vs [Check, Bet Nuts, Bluff, Bet All]
    ]
    
    for row in payoff:
        print([round(x, 3) for x in row])


if __name__ == "__main__":
    analyze_clairvoyance_payoffs()