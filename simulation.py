"""Simple real-time simulation of two AI factions competing."""
import random

class Player:
    def __init__(self, name):
        self.name = name
        self.fort_hp = 20
        self.units = 3
        self.gold = 0
        self.farms = 0

    def decide_actions(self, enemy):
        """Return a dict describing actions for this tick."""
        actions = {
            'attack': 0,
            'build_farm': False,
            'recruit': 0,
        }
        # Build farms first if possible (cost 10 gold)
        if self.gold >= 10 and self.farms < 3:
            actions['build_farm'] = True
        # Recruit units with remaining gold (cost 5 gold each)
        remaining_gold = self.gold - (10 if actions['build_farm'] else 0)
        while remaining_gold >= 5 and self.units + actions['recruit'] < 10:
            actions['recruit'] += 1
            remaining_gold -= 5
        # Attack if we have an advantage or occasionally at random
        if self.units > enemy.units and self.units > 0:
            actions["attack"] = self.units // 2
        elif self.units == enemy.units and self.units > 0 and random.random() < 0.3:
            actions["attack"] = self.units // 2
        return actions

    def perform_actions(self, actions):
        if actions['build_farm'] and self.gold >= 10:
            self.gold -= 10
            self.farms += 1
        for _ in range(actions['recruit']):
            if self.gold >= 5:
                self.gold -= 5
                self.units += 1

    def gather_gold(self, gatherers):
        self.gold += gatherers + self.farms

    def take_damage(self, damage):
        self.fort_hp -= damage

class Game:
    def __init__(self):
        self.players = [Player('A'), Player('B')]
        self.tick_count = 0

    def run(self, max_ticks=50):
        while (all(p.fort_hp > 0 and p.units > 0 for p in self.players)
               and self.tick_count < max_ticks):
            self.tick_count += 1
            self.tick()
        self.print_winner()

    def tick(self):
        p1, p2 = self.players
        actions = [p1.decide_actions(p2), p2.decide_actions(p1)]
        for p, a in zip(self.players, actions):
            p.perform_actions(a)
        attackers = [min(p.units, a['attack']) for p, a in zip(self.players, actions)]
        gatherers = [p.units - atk for p, atk in zip(self.players, attackers)]
        for p, g in zip(self.players, gatherers):
            p.gather_gold(g)
        self.resolve_combat(attackers)
        self.print_tick(attackers)

    def resolve_combat(self, attackers):
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

    def print_tick(self, attackers):
        p1, p2 = self.players
        print(f"Tick {self.tick_count}")
        for p in self.players:
            print(f" Player {p.name}: units={p.units}, farms={p.farms}, gold={p.gold}, fort_hp={p.fort_hp}")
        print(f"  Attacks: A->{attackers[0]} men, B->{attackers[1]} men")
        print()

    def print_winner(self):
        p1, p2 = self.players
        if p1.fort_hp <= 0 or p1.units <= 0:
            print(f"Winner: Player {p2.name}")
        elif p2.fort_hp <= 0 or p2.units <= 0:
            print(f"Winner: Player {p1.name}")
        else:
            print("Draw: no winner")

if __name__ == '__main__':
    Game().run()
