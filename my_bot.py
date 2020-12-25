import asyncio
import random

from lia.enums import *
from lia.api import *
from lia import constants
from lia import math_util
from lia.bot import Bot
from lia.networking_client import connect


# Initial implementation keeps picking random locations on the map
# and sending units there. Worker units collect resources if they
# see them while warrior units shoot if they see opponents.
class MyBot(Bot):

    # This method is called 10 times per game second and holds current
    # game state. Use Api object to call actions on your units.
    # - GameState reference: https://docs.liagame.com/api/#gamestate
    # - Api reference:       https://docs.liagame.com/api/#api-object
    def update(self, state, api):

        # If you have enough resources to spawn a new warrior unit then spawn it.
        if state["resources"] >= constants.WARRIOR_PRICE:
            api.spawn_unit(UnitType.WARRIOR)

        # We iterate through all of our units that are still alive.
        for unit in state["units"]:
            # If the unit is not going anywhere, we send it
            # to a random valid location on the map.
            if len(unit["navigationPath"]) == 0:

                # Generate new x and y until you get a position on the map
                # where there is no obstacle.
                while True:
                    x = random.randint(0, constants.MAP_WIDTH - 1)
                    y = random.randint(0, constants.MAP_HEIGHT - 1)

                    # If map[x][y] equals false it means that at (x,y) there is no obstacle.
                    if constants.MAP[x][y] is False:
                        # Send the unit to (x, y)
                        api.navigation_start(unit["id"], x, y)
                        break

            # If the unit is a worker and it sees at least one resource
            # then make it go to the first resource to collect it.
            if unit["type"] == UnitType.WORKER and len(unit["resourcesInView"]) > 0:
                resource = unit["resourcesInView"][0]
                api.navigation_start(unit["id"], resource["x"], resource["y"])

            # If the unit is a warrior and it sees an opponent then make it shoot.
            if unit["type"] == UnitType.WARRIOR and len(unit["opponentsInView"]) > 0:
                api.shoot(unit["id"])
                api.say_something(unit["id"], "I see you!")


# Connects your bot to Lia game engine, don't change it.
if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(connect(MyBot()))
