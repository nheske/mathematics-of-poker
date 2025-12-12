from dataclasses import dataclass, field
from typing import Dict, List


# ---------- Information Set ----------

@dataclass
class InfoSet:
    key: str
    regret_sum: List[float] = field(default_factory=lambda: [0.0, 0.0])
    strategy_sum: List[float] = field(default_factory=lambda: [0.0, 0.0])

    def get_strategy(self, reach_prob: float) -> List[float]:
        """
        Regret-matching to get current strategy.
        reach_prob: reach probability for THIS player at this infoset
                    (used to accumulate average strategy).
        Returns: list of action probabilities [a0, a1].
        """
        normalizing_sum = 0.0
        strategy = [0.0, 0.0]

        # regret matching
        for a in range(2):
            strategy[a] = max(self.regret_sum[a], 0.0)
            normalizing_sum += strategy[a]

        if normalizing_sum > 0:
            for a in range(2):
                strategy[a] /= normalizing_sum
        else:
            # no positive regret: play uniform
            strategy = [0.5, 0.5]

        # accumulate strategy for computing average strategy
        for a in range(2):
            self.strategy_sum[a] += reach_prob * strategy[a]

        return strategy

    def get_average_strategy(self) -> List[float]:
        total = sum(self.strategy_sum)
        if total > 0:
            return [s / total for s in self.strategy_sum]
        else:
            # if never reached, default to uniform
            return [0.5, 0.5]


# ---------- Toy Game CFR Engine ----------

class ToyPokerCFR:
    """
    CFR for the one-street toy game from Ganzfried & Chiswick:
    - Deck: 1..n
    - P1 cards from p_dist, P2 from q_dist
    - Initial pot = pot_size
    - Single bet size = bet_size
    - No raises.
    """

    def __init__(self, p_dist, q_dist, pot_size: float = 1.0, bet_size: float = 1.0):
        assert len(p_dist) == len(q_dist)
        self.n_cards = len(p_dist)
        self.p_dist = p_dist  # distribution for P1
        self.q_dist = q_dist  # distribution for P2
        self.pot = pot_size
        self.bet = bet_size
        self.infosets: Dict[str, InfoSet] = {}

    # ----- Game tree helpers -----

    def _is_terminal(self, history: str) -> bool:
        # Explicit terminal histories:
        # "bf"  : P1 bet, P2 folds
        # "bc"  : P1 bet, P2 calls
        # "ck"  : P1 check, P2 check
        # "cbf" : P1 check, P2 bet, P1 folds
        # "cbc" : P1 check, P2 bet, P1 calls
        return history in ("bf", "bc", "ck", "cbf", "cbc")

    def _terminal_utility_p1(self, c1: int, c2: int, history: str) -> float:
        """
        Utility for Player 1 (P1) at a terminal node, given cards c1, c2.
        We treat pot as dead money; bets are from stacks.
        """
        P = self.pot
        b = self.bet

        def showdown_no_bet():
            # final pot = P
            if c1 > c2:
                return P          # P1 wins full pot
            elif c1 < c2:
                return 0.0        # P1 gets nothing
            else:
                return P / 2.0    # split pot

        def showdown_with_bet():
            # final pot = P + 2b, but each player has invested b
            # P1 net: +P + b if win, -b if lose, +P/2 if tie
            if c1 > c2:
                return P + b
            elif c1 < c2:
                return -b
            else:
                return P / 2.0

        if history == "bf":   # P1 bet, P2 folds
            return P
        if history == "bc":   # P1 bet, P2 calls
            return showdown_with_bet()
        if history == "ck":   # P1 check, P2 check
            return showdown_no_bet()
        if history == "cbf":  # P1 check, P2 bets, P1 folds
            return -P
        if history == "cbc":  # P1 check, P2 bets, P1 calls
            return showdown_with_bet()

        raise ValueError(f"Unknown terminal history: {history}")

    def _acting_player(self, history: str) -> int:
        """
        0 = P1, 1 = P2.
        - ""   : P1 acts (bet/check)
        - "b"  : P2 acts (call/fold vs P1 bet)
        - "c"  : P2 acts (bet/check after P1 check)
        - "cb" : P1 acts (call/fold vs P2 bet)
        """
        if history in ("", "cb"):
            return 0
        elif history in ("b", "c"):
            return 1
        raise ValueError(f"Invalid non-terminal history: {history}")

    def _actions(self, history: str):
        """
        Return list of action labels for this node.
        We always have 2 actions:
        - ""   (P1): ["b", "c"]  bet / check
        - "b"  (P2): ["c", "f"]  call / fold
        - "c"  (P2): ["b", "k"]  bet / check
        - "cb" (P1): ["c", "f"]  call / fold
        """
        if history == "":
            return ["b", "c"]
        if history == "b":
            return ["c", "f"]
        if history == "c":
            return ["b", "k"]
        if history == "cb":
            return ["c", "f"]
        raise ValueError(f"No actions defined for history: {history}")

    def _next_history(self, history: str, action: str) -> str:
        """
        Deterministic transition to next history
        given the current history and chosen action.
        """
        if history == "":
            if action == "b":  # P1 bets
                return "b"
            elif action == "c":  # P1 checks
                return "c"

        elif history == "b":  # P2 vs P1 bet
            if action == "c":
                return "bc"   # call → showdown
            elif action == "f":
                return "bf"   # fold

        elif history == "c":  # P2 after P1 check
            if action == "b":
                return "cb"   # P2 bets, P1 to act
            elif action == "k":
                return "ck"   # check/check → showdown

        elif history == "cb":  # P1 vs P2 bet after a check
            if action == "c":
                return "cbc"  # call → showdown
            elif action == "f":
                return "cbf"  # fold

        raise ValueError(f"Invalid transition from history={history}, action={action}")

    def _get_infoset(self, player: int, card: int, history: str) -> InfoSet:
        """
        Information set is defined by:
        - player (0 or 1)
        - this player's private card
        - public betting history
        """
        key = f"P{player}|{card}|{history}"
        if key not in self.infosets:
            self.infosets[key] = InfoSet(key=key)
        return self.infosets[key]

    # ----- CFR recursion -----

    def cfr(self, c1: int, c2: int, history: str, p0: float, p1: float) -> float:
        """
        Counterfactual regret minimization recursion.

        c1, c2 are card *values* in {1..n_cards}.
        p0, p1 are reach probabilities (including chance weight) for P1 and P2
        up to this node.

        Returns:
            utility for the *current player* at this node (with sign handled
            so that recursion always returns value from the viewpoint of the
            player who just played here).
        """
        # Terminal node
        if self._is_terminal(history):
            return self._terminal_utility_p1(c1, c2, history)

        player = self._acting_player(history)
        card = c1 if player == 0 else c2
        infoset = self._get_infoset(player, card, history)
        reach_prob = p0 if player == 0 else p1

        strategy = infoset.get_strategy(reach_prob)
        actions = self._actions(history)

        util = [0.0, 0.0]
        node_util = 0.0

        for a_idx, action in enumerate(actions):
            next_hist = self._next_history(history, action)
            if player == 0:
                # P1 acts: child utility is from P1's perspective
                util[a_idx] = self.cfr(c1, c2, next_hist,
                                       p0 * strategy[a_idx], p1)
            else:
                # P2 acts: we flip sign so util[a] is from P2's perspective
                util[a_idx] = -self.cfr(c1, c2, next_hist,
                                        p0, p1 * strategy[a_idx])

            node_util += strategy[a_idx] * util[a_idx]

        # Regret update (always from *current player's* perspective)
        for a_idx in range(2):
            regret = util[a_idx] - node_util
            if player == 0:
                # scale by opponent reach (p1)
                infoset.regret_sum[a_idx] += p1 * regret
            else:
                # scale by opponent reach (p0)
                infoset.regret_sum[a_idx] += p0 * regret

        # Keep perspective consistent for upstream caller: always return value as P1 sees it.
        return node_util if player == 0 else -node_util

    # ----- Training and analysis -----

    def train(self, iterations: int = 10000):
        """
        Run CFR for given number of iterations.
        We loop over *all* card pairs (c1, c2) each iteration,
        weighted by their chance probabilities p_dist[c1] * q_dist[c2].
        """
        for _ in range(iterations):
            for i in range(self.n_cards):
                for j in range(self.n_cards):
                    w = self.p_dist[i] * self.q_dist[j]
                    if w == 0.0:
                        continue
                    # c1, c2 are 1..n instead of 0..n-1
                    self.cfr(i + 1, j + 1, "", w, w)

    def get_average_strategies(self) -> Dict[str, List[float]]:
        """
        Returns a dict: infoset_key -> [prob(action0), prob(action1)]
        where action mapping depends on history:
        - history ""
            actions: ["b", "c"] (P1 bet / check)
        - history "b"
            actions: ["c", "f"] (P2 call / fold vs P1 bet)
        - history "c"
            actions: ["b", "k"] (P2 bet / check after P1 check)
        - history "cb"
            actions: ["c", "f"] (P1 call / fold vs P2 bet)
        """
        return {k: infoset.get_average_strategy()
                for k, infoset in self.infosets.items()}

    def compute_range_advantage(self) -> float:
        """
        Range Advantage for P1 as defined in the paper:
        RA = P(c1 > c2) + 0.5 * P(c1 == c2)
        using the distributions p_dist (P1) and q_dist (P2).
        """
        eq = 0.0
        tie = 0.0
        for i in range(self.n_cards):
            for j in range(self.n_cards):
                w = self.p_dist[i] * self.q_dist[j]
                if i > j:
                    eq += w
                elif i == j:
                    tie += w
        ra = eq + 0.5 * tie
        return ra

    def compute_odf_vs_p1_bet(self) -> float:
        """
        Optimal Defense Frequency (ODF) vs P1's initial bet.

        c(j) = P2's call frequency with card j when facing history "b".
        ODF = sum_j q_j * c(j).
        """
        odf = 0.0
        for j in range(self.n_cards):
            key = f"P1|{j+1}|b"  # player 1 (P2), card=j+1, history="b"
            infoset = self.infosets.get(key)
            if infoset is None:
                continue  # never reached in training
            avg_strategy = infoset.get_average_strategy()
            call_prob = avg_strategy[0]  # index 0 = "c" = call
            odf += self.q_dist[j] * call_prob
        return odf
