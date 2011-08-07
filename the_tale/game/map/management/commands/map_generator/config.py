# -*- coding: utf-8 -*-

##############################################################
# Constant part
##############################################################

City = places.City
TERRAIN = constants.TERRAIN

##############################################################
# Modified part
##############################################################

map_width = 30
map_height = 20

places_list = [
    City(x=1,  y=1,  significance=1,  terrain=TERRAIN.DESERT),
    City(x=14, y=1,  significance=1,  terrain=TERRAIN.FOREST),
    City(x=27, y=1,  significance=6,  terrain=TERRAIN.SWAMP),
    City(x=5,  y=3,  significance=5,  terrain=TERRAIN.DESERT),

    City(x=19, y=5,  significance=3,  terrain=TERRAIN.FOREST),
    City(x=11, y=6,  significance=4,  terrain=TERRAIN.DESERT),
    City(x=20, y=8,  significance=9,  terrain=TERRAIN.GRASS),
    City(x=24, y=8,  significance=12, terrain=TERRAIN.FOREST),

    City(x=1,  y=9,  significance=6,  terrain=TERRAIN.FOREST),
    City(x=11, y=11, significance=4,  terrain=TERRAIN.SWAMP),
    City(x=5,  y=12, significance=1,  terrain=TERRAIN.GRASS),
    City(x=17, y=12, significance=2,  terrain=TERRAIN.GRASS),

    City(x=24, y=13, significance=1,  terrain=TERRAIN.FOREST),
    City(x=27, y=13, significance=1,  terrain=TERRAIN.GRASS),
    City(x=3,  y=17, significance=10, terrain=TERRAIN.GRASS),
    City(x=10, y=18, significance=3, terrain=TERRAIN.FOREST),
    City(x=19, y=17, significance=8, terrain=TERRAIN.SWAMP),
    City(x=28, y=19, significance=3, terrain=TERRAIN.SWAMP)
]
