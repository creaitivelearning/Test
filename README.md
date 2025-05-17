# AI Faction Simulation

This repository contains a simple Python simulation where two AI-controlled factions compete in real time. Each faction starts with a fort and three men. Men can gather gold, build farms, recruit additional men, and attack the opposing fort.

Key features:

- Configurable farm and unit costs
- Optional random seed for reproducible games
- More detailed tick-by-tick output

To run the simulation:

```bash
python3 simulation.py [--farm-cost NUM] [--unit-cost NUM] [--seed NUM] [--max-ticks NUM]
```

The game proceeds in ticks until one fort is destroyed or a side runs out of units. Optional arguments allow you to tweak costs, control the random seed, and set a maximum number of ticks. The output shows each tick's state and announces the winner.
