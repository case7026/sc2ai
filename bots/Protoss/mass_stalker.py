import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import NEXUS, PROBE, PYLON, ASSIMILATOR, GATEWAY, STALKER, CYBERNETICSCORE

import random

class MassStalker(sc2.BotAI):
    async def on_step(self, iteration):
        await self.distribute_workers()
        await self.build_workers()
        await self.build_pylons()
        await self.expand()
        await self.build_assimilator()
        await self.build_offensive_buildings()
        await self.build_stalkers()
        await self.three_stalker_harrass()
        
    async def build_workers(self):
        for nexus in self.units(NEXUS).ready.noqueue:
            if self.can_afford(PROBE):
                await self.do(nexus.train(PROBE))

    async def build_pylons(self):
        if self.supply_left < 3 and not self.already_pending(PYLON):
            nexuses = self.units(NEXUS).ready
            if nexuses.exists:
                if self.can_afford(PYLON):
                        await self.build(PYLON, near=nexuses.first)

    async def expand(self):
        if self.units(NEXUS).amount < 2 and self.can_afford(NEXUS):
            await self.expand_now()

    async def build_assimilator(self):
        for nexus in self.units(NEXUS).ready:
            vespene_geysers = self.state.vespene_geyser.closer_than(10.0, nexus)
            for vespene_geyser in vespene_geysers:
                if not self.can_afford(ASSIMILATOR):
                    break
                worker = self.select_build_worker(vespene_geyser.position)
                if worker is None:
                    break
                if not self.units(ASSIMILATOR).closer_than(1.0, vespene_geyser).exists:
                    await self.do(worker.build(ASSIMILATOR, vespene_geyser))

    async def build_offensive_buildings(self):
        if self.units(PYLON).ready.exists:
            pylon = self.units(PYLON).ready.random
            if self.units(GATEWAY).ready.exists:
                if not self.units(CYBERNETICSCORE):
                    if self.can_afford(CYBERNETICSCORE) and not self.already_pending(CYBERNETICSCORE):
                        await self.build(CYBERNETICSCORE, near=pylon)
            else:
                await self.build(GATEWAY, near=pylon)

    async def build_stalkers(self):
        for gw in self.units(GATEWAY).ready.noqueue:
            if self.can_afford(STALKER) and self.units(CYBERNETICSCORE).exists and self.supply_left > 2:
                await self.do(gw.train(STALKER))

    async def three_stalker_harrass(self):
        if self.units(STALKER).ready.amount > 10:
            for stalker in self.units(STALKER).idle:
                await self.do(stalker.attack(self.find_target(self.state)))
        elif self.units(STALKER).ready.amount > 0:
            if len(self.known_enemy_units) > 0:
                for stalker in self.units(STALKER).idle:
                    await self.do(stalker.attack(random.choice(self.known_enemy_units)))

    def find_target(self, state):
        if len(self.known_enemy_units) > 0:
            return random.choice(self.known_enemy_units)
        elif len(self.known_enemy_structures) > 0:
            return random.choice(self.known_enemy_structures)
        else:
            return self.enemy_start_locations[0]

run_game(maps.get("CyberForestLE"), [
    Bot(Race.Protoss  , MassStalker()),
    Computer(Race.Zerg, Difficulty.Easy)
], realtime=False)