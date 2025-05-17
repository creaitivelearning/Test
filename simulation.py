"""Simple real-time simulation of two AI factions competing."""
import argparse
import random
from dataclasses import dataclass
from typing import Dict

@dataclass
class Player:
    """Represents one side in the simulation."""

    name: str
    fort_hp: int = 20
    units: int = 3
    gold: int = 0
    farms: int = 0

    def decide_actions(self, enemy: "Player", farm_cost: int, unit_cost: int) -> Dict[str, int | bool]:
        """Return a dict describing actions for this tick."""
        actions: Dict[str, int | bool] = {
            "attack": 0,
            "build_farm": False,
            "recruit": 0,
        }
        # Build farms first if possible
        if self.gold >= farm_cost and self.farms < 3:
            actions["build_farm"] = True
        # Recruit units with remaining gold
        remaining_gold = self.gold - (farm_cost if actions["build_farm"] else 0)
        while remaining_gold >= unit_cost and self.units + actions["recruit"] < 10:
            actions["recruit"] += 1
            remaining_gold -= unit_cost
        # Attack if we have an advantage or occasionally at random
        if self.units > enemy.units and self.units > 0:
            actions["attack"] = self.units // 2
        elif self.units == enemy.units and self.units > 0 and random.random() < 0.3:
            actions["attack"] = self.units // 2
        return actions

    def perform_actions(self, actions: Dict[str, int | bool], farm_cost: int, unit_cost: int) -> None:
        if actions["build_farm"] and self.gold >= farm_cost:
            self.gold -= farm_cost
            self.farms += 1
        for _ in range(actions["recruit"]):
            if self.gold >= unit_cost:
                self.gold -= unit_cost
                self.units += 1

    def gather_gold(self, gatherers: int) -> None:
        self.gold += gatherers + self.farms

    def take_damage(self, damage: int) -> None:
        self.fort_hp -= damage

class Game:
    def __init__(self, farm_cost: int = 10, unit_cost: int = 5):
        self.players = [Player("A"), Player("B")]
        self.tick_count = 0
        self.farm_cost = farm_cost
        self.unit_cost = unit_cost

    def run(self, max_ticks: int = 50) -> None:
        while (all(p.fort_hp > 0 and p.units > 0 for p in self.players)
               and self.tick_count < max_ticks):
            self.tick_count += 1
            self.tick()
        self.print_winner()

    def tick(self) -> None:
        p1, p2 = self.players
        actions = [
            p1.decide_actions(p2, self.farm_cost, self.unit_cost),
            p2.decide_actions(p1, self.farm_cost, self.unit_cost),
        ]
        for p, a in zip(self.players, actions):
            p.perform_actions(a, self.farm_cost, self.unit_cost)
        attackers = [min(p.units, a['attack']) for p, a in zip(self.players, actions)]
        gatherers = [p.units - atk for p, atk in zip(self.players, attackers)]
        for p, g in zip(self.players, gatherers):
            p.gather_gold(g)
        self.resolve_combat(attackers)
        self.print_tick(attackers, actions)

    def resolve_combat(self, attackers) -> None:
        p1, p2 = self.players
        atk1, atk2 = attackers
        kills_on_p2 = min(atk1, p2.units)
        kills_on_p1 = min(atk2, p1.units)
        p2.units -= kills_on_p2
        p1.units -= kills_on_p1
        if atk1 > kills_on_p2:
            p2.take_damage(atk1 - kills_on_p2)
        if atk2 > kills_on_p1:
            p1.take_damage(atk2 - kills_on_p1)

    def print_tick(self, attackers, actions) -> None:
        print(f"Tick {self.tick_count}")
        for p, a in zip(self.players, actions):
            farm_txt = "built farm" if a["build_farm"] else "no farm"
            print(
                f" Player {p.name}: units={p.units}, farms={p.farms}, "
                f"gold={p.gold}, fort_hp={p.fort_hp} "
                f"(recruited {a['recruit']}, {farm_txt})"
            )
        print(f"  Attacks: A->{attackers[0]} men, B->{attackers[1]} men")
        print()

    def print_winner(self) -> None:
        p1, p2 = self.players
        if p1.fort_hp <= 0 or p1.units <= 0:
            print(f"Winner: Player {p2.name}")
        elif p2.fort_hp <= 0 or p2.units <= 0:
            print(f"Winner: Player {p1.name}")
        else:
            print("Draw: no winner")

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AI Faction Simulation")
    parser.add_argument("--farm-cost", type=int, default=10, help="Gold cost of building a farm")
    parser.add_argument("--unit-cost", type=int, default=5, help="Gold cost of recruiting a unit")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for deterministic runs")
    parser.add_argument("--max-ticks", type=int, default=50, help="Maximum number of ticks to simulate")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.seed is not None:
        random.seed(args.seed)
    Game(farm_cost=args.farm_cost, unit_cost=args.unit_cost).run(max_ticks=args.max_ticks)
