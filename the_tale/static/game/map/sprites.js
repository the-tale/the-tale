

pgf.tilesets = {

    tileset3: {
        TILE_SIZE: 32,

        sprites: {
            'f': { src: "/tmp/map3.png",
                   x: 4 * 32,
                   y: 0 * 32,
                   w: 32,
                   h: 32
                 },
            '.': { src: "/tmp/map3.png",
                   x: 0 * 32,
                   y: 0 * 32,
                   w: 32,
                   h: 32
                 },
            '_': { src: "/tmp/map3.png",
                   x: 3 * 32,
                   y: 0 * 32,
                   w: 32,
                   h: 32
                 },
            'w': { src: "/tmp/map3.png",
                   x: 2 * 32,
                   y: 0 * 32,
                   w: 32,
                   h: 32
                 },
            'place': { src: "/tmp/map3.png",
                       x: 2 * 32,
                       y: 6 * 32,
                       w: 32,
                       h: 32
                     },
            'hero': { src: "/tmp/map3.png",
                      x: 7 * 32,
                      y: 0 * 32,
                      w: 32,
                      h: 32
                    },
            'r': { src: "/tmp/map_road.png",
                   x: 0 * 32,
                   y: 0 * 32,
                   w: 32,
                   h: 32
                 },
        },
    },

    tileset2: {

        TILE_SIZE: 32,

        sprites: {
            'f': { src: "/tmp/map2.png",
                   x: 1 * 32,
                   y: 0 * 32,
                   w: 32,
                   h: 32
                 },
            '.': { src: "/tmp/map2.png",
                   x: 3 * 32,
                   y: 0 * 32,
                   w: 32,
                   h: 32
                 },
            '_': { src: "/tmp/map2.png",
                   x: 1 * 32,
                   y: 2 * 32,
                   w: 32,
                   h: 32
                 },
            'w': { src: "/tmp/map2.png",
                   x: 7 * 32,
                   y: 4 * 32,
                   w: 32,
                   h: 32
                 },
            'place_small': { src: "/tmp/city_small.png",
                       x: 0,
                       y: 0,
                       w: 32,
                       h: 32
                     },
            'place_medium': { src: "/tmp/city_medium.png",
                       x: 0,
                       y: 0,
                       w: 32,
                       h: 32
                     },
            'place_large': { src: "/tmp/city_large.png",
                       x: 0,
                       y: 0,
                       w: 32,
                       h: 32
                     },
            'hero_right': { src: "/tmp/hero.png",
                            x: 0,
                            y: 0,
                            w: 32,
                            h: 32
                    },
            'hero_left': { src: "/tmp/hero.png",
                           x: 32,
                           y: 0,
                           w: 32,
                           h: 32
                    },
            'r4': { src: "/tmp/map_road.png",
                   x: 0 * 32,
                   y: 0 * 32,
                   w: 32,
                   h: 32
                 },
            'r3': { src: "/tmp/map_road.png",
                   x: 1 * 32,
                   y: 0 * 32,
                   w: 32,
                   h: 32
                 },
            'r_line': { src: "/tmp/map_road.png",
                        x: 2 * 32,
                        y: 0 * 32,
                        w: 32,
                        h: 32
                      },
            'r_angle': { src: "/tmp/map_road.png",
                         x: 3 * 32,
                         y: 0 * 32,
                         w: 32,
                         h: 32
                       },
        },
    },

    tileset1: {

        TILE_SIZE: 48,
        
        sprites: {
            'f': { src: "/tmp/map.png",
                   x: 3 * 48,
                   y: 0 * 48,
                   w: 48,
                   h: 48
                 },
            '.': { src: "/tmp/map.png",
                   x: 0 * 48,
                   y: 0 * 48,
                   w: 48,
                   h: 48
                 },
            '_': { src: "/tmp/map.png",
                   x: 0 * 48,
                   y: 3 * 48,
                   w: 48,
                   h: 48
                 },
            'w': { src: "/tmp/map.png",
                   x: 14 * 48,
                   y: 2 * 48,
                   w: 48,
                   h: 48
                 },
            'place': { src: "/tmp/map.png",
                       x: 4 * 48,
                       y: 4 * 48,
                       w: 48,
                       h: 48
                     },
            'hero': { src: "/tmp/map.png",
                      x: 5 * 48,
                      y: 11 * 48,
                      w: 48,
                      h: 48
                    },
        }
    }
}
