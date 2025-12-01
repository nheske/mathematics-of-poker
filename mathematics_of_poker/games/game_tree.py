from __future__ import annotations

"""Extensive-form game tree primitives used for Monte Carlo CFR."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Iterable, List, Optional, Tuple


class Player(Enum):
    """Two-player zero-sum game participants plus chance."""

    X = "x"
    Y = "y"
    CHANCE = "chance"
    TERMINAL = "terminal"


@dataclass
class InformationSet:
    """Collection of decision nodes that share the same information."""

    key: str
    player: Player
    description: Optional[str] = None
    nodes: List["GameTreeNode"] = field(default_factory=list, init=False)

    def add_node(self, node: "GameTreeNode") -> None:
        self.nodes.append(node)


@dataclass
class GameTreeEdge:
    """Action edge leaving a node."""

    action: str
    child: "GameTreeNode"
    probability: float = 1.0
    metadata: Optional[Dict[str, object]] = None


@dataclass
class GameTreeNode:
    """A node in an extensive-form game tree."""

    player: Player
    info_set: Optional[InformationSet] = None
    payoffs: Optional[Tuple[float, float]] = None
    edges: List[GameTreeEdge] = field(default_factory=list)
    parent: Optional["GameTreeNode"] = None
    action_from_parent: Optional[str] = None

    def add_child(
        self,
        action: str,
        child: "GameTreeNode",
        probability: float = 1.0,
        metadata: Optional[Dict[str, object]] = None,
    ) -> None:
        """Attach a child edge to the node."""
        child.parent = self
        child.action_from_parent = action
        self.edges.append(
            GameTreeEdge(action=action, child=child, probability=probability, metadata=metadata)
        )

    @property
    def is_terminal(self) -> bool:
        return self.payoffs is not None

    def iter_children(self) -> Iterable[GameTreeEdge]:
        return list(self.edges)


@dataclass
class GameTree:
    """Container for an extensive-form game tree and its information sets."""

    root: GameTreeNode
    information_sets: Dict[str, InformationSet]

    def all_information_sets(self) -> Iterable[InformationSet]:
        return self.information_sets.values()

    def dump(self) -> str:
        """Return a human-readable dump of the tree for debugging."""

        lines: List[str] = []

        def recurse(node: GameTreeNode, depth: int = 0) -> None:
            indent = "  " * depth
            if node.is_terminal:
                lines.append(f"{indent}Terminal payoffs={node.payoffs}")
                return

            role = node.player.value if isinstance(node.player, Player) else str(node.player)
            info = f" info={node.info_set.key}" if node.info_set else ""
            lines.append(f"{indent}{role}{info}")

            for edge in node.edges:
                meta = f" {edge.metadata}" if edge.metadata else ""
                lines.append(
                    f"{indent}  --{edge.action} (p={edge.probability:.3f}){meta}"
                )
                recurse(edge.child, depth + 2)

        recurse(self.root)
        return "\n".join(lines)


@dataclass(frozen=True)
class ChanceDistribution:
    """Utility helper to describe chance outcomes."""

    outcomes: Tuple[Tuple[str, float], ...]

    def __iter__(self):
        return iter(self.outcomes)

    def validate(self) -> None:
        total = sum(prob for _, prob in self.outcomes)
        if not (abs(total - 1.0) <= 1e-9):
            raise ValueError("Chance probabilities must sum to 1.0")
