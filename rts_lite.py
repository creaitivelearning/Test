"""Expanded RTS-like simulation with buildings, units, and simple AI."""
import random


class Building:
    COSTS = {
        'fort': 0,
        'mine': 100,
        'house': 50,
        'barracks': 150,
        'tower': 200,
    }

    def __init__(self, owner, btype):
        self.owner = owner
        self.type = btype
        self.hp = self._set_hp(btype)

    def _set_hp(self, btype):
        return {
            'fort': 500,
            'mine': 100,
            'house': 80,
            'barracks': 150,
            'tower': 200,
        }[btype]

    def income(self):
        return 10 if self.type == 'mine' else 0


class Unit:
    def __init__(self, owner, role='scavenger'):
        self.owner = owner
        self.role = role
        self.hp = 100

    def is_alive(self):
        return self.hp > 0


class Player:
    def __init__(self, name):
        self.name = name
        self.money = 100
        self.units = []
        self.buildings = []
        self.population_cap = 3
        self.ai = AIController(self)
        self.init_starting_assets()

    def init_starting_assets(self):
        self.buildings.append(Building(self, 'fort'))
        for _ in range(3):
            self.units.append(Unit(self, 'scavenger'))

    @property
    def fort(self):
        for b in self.buildings:
            if b.type == 'fort':
                return b
        return None

    def income(self):
        total = sum(b.income() for b in self.buildings)
        total += sum(1 for u in self.units if u.role == 'scavenger')
        self.money += total

    def train_unit(self, role='scavenger'):
        cost = 20 if role == 'fighter' else 15
        if len(self.units) >= self.population_cap or self.money < cost:
            return False
        self.money -= cost
        self.units.append(Unit(self, role))
        return True

    def build_structure(self, btype):
        cost = Building.COSTS[btype]
        if self.money < cost:
            return False
        self.money -= cost
        self.buildings.append(Building(self, btype))
        if btype == 'house':
            self.population_cap += 2
        return True

    def living_units(self):
        return [u for u in self.units if u.is_alive()]

    def alive(self):
        return self.fort and self.fort.hp > 0


class AIController:
    def __init__(self, player):
        self.player = player

    def decide(self, enemy):
        p = self.player
        # Build mines first up to 2
        mines = sum(1 for b in p.buildings if b.type == 'mine')
        if p.money >= Building.COSTS['mine'] and mines < 2:
            p.build_structure('mine')
            return
        # Keep population growing
        if len(p.units) >= p.population_cap and p.money >= Building.COSTS['house']:
            p.build_structure('house')
            return
        # Train fighters if we have barracks else build one
        if not any(b.type == 'barracks' for b in p.buildings):
            if p.money >= Building.COSTS['barracks']:
                p.build_structure('barracks')
            return
        # Train units
        if len(p.units) < p.population_cap:
            role = 'fighter' if random.random() < 0.5 else 'scavenger'
            p.train_unit(role)
            return
        # Decide to attack if stronger
        fighters = [u for u in p.units if u.role == 'fighter' and u.is_alive()]
        enemy_fighters = [u for u in enemy.units if u.role == 'fighter' and u.is_alive()]
        if len(fighters) > len(enemy_fighters) + 2:
            self.attack(enemy)

    def attack(self, enemy):
        attackers = [u for u in self.player.units if u.role == 'fighter' and u.is_alive()]
        defenders = [u for u in enemy.units if u.role == 'fighter' and u.is_alive()]
        while attackers and defenders:
            defenders.pop().hp = 0
            attackers.pop().hp = 0
        # remaining attackers damage fort
        dmg = len([u for u in attackers if u.is_alive()]) * 10
        enemy.fort.hp -= dmg


class Game:
    def __init__(self, players=2):
        names = [chr(ord('A') + i) for i in range(players)]
        self.players = [Player(n) for n in names]
        self.tick = 0

    def living_players(self):
        return [p for p in self.players if p.alive()]

    def run(self, max_ticks=100):
        while len(self.living_players()) > 1 and self.tick < max_ticks:
            self.tick += 1
            self.step()
        self.print_winner()

    def step(self):
        p1, p2 = self.players
        p1.ai.decide(p2)
        p2.ai.decide(p1)
        for p in self.players:
            p.income()
        self.print_state()

    def print_state(self):
        print(f"Tick {self.tick}")
        for p in self.players:
            fighters = sum(1 for u in p.units if u.role == 'fighter' and u.is_alive())
            scavengers = sum(1 for u in p.units if u.role == 'scavenger' and u.is_alive())
            print(
                f" Player {p.name}: money={p.money}, fighters={fighters}, scavengers={scavengers}, fort_hp={p.fort.hp}"
            )
        print()

    def print_winner(self):
        alive = [p for p in self.players if p.alive()]
        if len(alive) == 1:
            print(f"Winner: Player {alive[0].name}")
        else:
            print("Draw")


if __name__ == '__main__':
    Game().run()
