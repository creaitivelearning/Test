# AI Faction Simulation

This repository contains small Python simulations where AI-controlled factions compete.

## Basic Simulation
The original example is in `simulation.py`. Two factions gather gold, build farms, recruit units and attack each other's fort.

Run it with:

```bash
python3 simulation.py
```

## Expanded RTS-Lite
The file `rts_lite.py` introduces buildings, unit roles, and a slightly smarter AI. Players can build mines, houses, and barracks, train fighter or scavenger units, and attack when they gain an advantage.

Run it with:

```bash
python3 rts_lite.py
```

Both simulations print tick-by-tick logs until one fort falls or the tick limit is reached.
