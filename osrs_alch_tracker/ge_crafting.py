"""
OSRS Grand Exchange Production & Crafting Moneymaking Database.
Contains processing and production recipes across Herblore, Fletching, Smithing, Crafting, Cooking, and Magic
designed specifically for purchasing materials on the Grand Exchange, crafting, and selling the finished
products back onto the Grand Exchange for pure gold profit.
"""

GE_PROFIT_RECIPES = [
    {
        "name": "Prayer potion(3)",
        "skill": "Herblore",
        "level": 38,
        "xp": 87.5,
        "output_id": 139,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 2200,
        "materials": [
            {
                "name": "Ranarr potion (unf)",
                "id": 99,
                "qty": 1
            },
            {
                "name": "Snape grass",
                "id": 231,
                "qty": 1
            }
        ]
    },
    {
        "name": "Super restore(3)",
        "skill": "Herblore",
        "level": 63,
        "xp": 142.5,
        "output_id": 3024,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 2200,
        "materials": [
            {
                "name": "Snapdragon potion (unf)",
                "id": 3004,
                "qty": 1
            },
            {
                "name": "Red spiders' eggs",
                "id": 223,
                "qty": 1
            }
        ]
    },
    {
        "name": "Saradomin brew(3)",
        "skill": "Herblore",
        "level": 81,
        "xp": 180.0,
        "output_id": 6685,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 2200,
        "materials": [
            {
                "name": "Toadflax potion (unf)",
                "id": 3002,
                "qty": 1
            },
            {
                "name": "Crushed nest",
                "id": 6693,
                "qty": 1
            }
        ]
    },
    {
        "name": "Super combat potion(4)",
        "skill": "Herblore",
        "level": 90,
        "xp": 150.0,
        "output_id": 12695,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 2000,
        "materials": [
            {
                "name": "Super attack(4)",
                "id": 2436,
                "qty": 1
            },
            {
                "name": "Super strength(4)",
                "id": 2440,
                "qty": 1
            },
            {
                "name": "Super defence(4)",
                "id": 2442,
                "qty": 1
            },
            {
                "name": "Torstol",
                "id": 269,
                "qty": 1
            }
        ]
    },
    {
        "name": "Stamina potion(4)",
        "skill": "Herblore",
        "level": 77,
        "xp": 102.0,
        "output_id": 12625,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 2200,
        "materials": [
            {
                "name": "Super energy(4)",
                "id": 3016,
                "qty": 1
            },
            {
                "name": "Amylase crystal",
                "id": 12640,
                "qty": 4
            }
        ]
    },
    {
        "name": "Extended antifire(4)",
        "skill": "Herblore",
        "level": 84,
        "xp": 110.0,
        "output_id": 11951,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 2200,
        "materials": [
            {
                "name": "Antifire potion(4)",
                "id": 2452,
                "qty": 1
            },
            {
                "name": "Lava scale shard",
                "id": 11994,
                "qty": 4
            }
        ]
    },
    {
        "name": "Bastion potion(3)",
        "skill": "Herblore",
        "level": 80,
        "xp": 155.0,
        "output_id": 22464,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 2200,
        "materials": [
            {
                "name": "Cadantine potion (unf)",
                "id": 107,
                "qty": 1
            },
            {
                "name": "Vial of blood",
                "id": 22446,
                "qty": 1
            },
            {
                "name": "Wine of zamorak",
                "id": 245,
                "qty": 1
            }
        ]
    },
    {
        "name": "Super attack(3)",
        "skill": "Herblore",
        "level": 45,
        "xp": 100.0,
        "output_id": 145,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 2200,
        "materials": [
            {
                "name": "Irit potion (unf)",
                "id": 101,
                "qty": 1
            },
            {
                "name": "Eye of newt",
                "id": 221,
                "qty": 1
            }
        ]
    },
    {
        "name": "Super strength(3)",
        "skill": "Herblore",
        "level": 55,
        "xp": 125.0,
        "output_id": 157,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 2200,
        "materials": [
            {
                "name": "Kwuarm potion (unf)",
                "id": 103,
                "qty": 1
            },
            {
                "name": "Limpwurt root",
                "id": 225,
                "qty": 1
            }
        ]
    },
    {
        "name": "Super defence(3)",
        "skill": "Herblore",
        "level": 66,
        "xp": 150.0,
        "output_id": 163,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 2200,
        "materials": [
            {
                "name": "Cadantine potion (unf)",
                "id": 107,
                "qty": 1
            },
            {
                "name": "White berries",
                "id": 239,
                "qty": 1
            }
        ]
    },
    {
        "name": "Ranging potion(3)",
        "skill": "Herblore",
        "level": 72,
        "xp": 162.5,
        "output_id": 169,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 2200,
        "materials": [
            {
                "name": "Dwarf weed potion (unf)",
                "id": 109,
                "qty": 1
            },
            {
                "name": "Wine of zamorak",
                "id": 245,
                "qty": 1
            }
        ]
    },
    {
        "name": "Magic potion(3)",
        "skill": "Herblore",
        "level": 76,
        "xp": 172.5,
        "output_id": 3042,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 2200,
        "materials": [
            {
                "name": "Lantadyme potion (unf)",
                "id": 2483,
                "qty": 1
            },
            {
                "name": "Potato cactus",
                "id": 3138,
                "qty": 1
            }
        ]
    },
    {
        "name": "Antifire potion(3)",
        "skill": "Herblore",
        "level": 69,
        "xp": 157.5,
        "output_id": 2454,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 2200,
        "materials": [
            {
                "name": "Lantadyme potion (unf)",
                "id": 2483,
                "qty": 1
            },
            {
                "name": "Dragon scale dust",
                "id": 241,
                "qty": 1
            }
        ]
    },
    {
        "name": "Energy potion(3)",
        "skill": "Herblore",
        "level": 26,
        "xp": 67.5,
        "output_id": 3010,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 2200,
        "materials": [
            {
                "name": "Harralander potion (unf)",
                "id": 97,
                "qty": 1
            },
            {
                "name": "Chocolate dust",
                "id": 1975,
                "qty": 1
            }
        ]
    },
    {
        "name": "Ranarr potion (unf)",
        "skill": "Herblore",
        "level": 30,
        "xp": 0.0,
        "output_id": 99,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 2800,
        "materials": [
            {
                "name": "Clean ranarr weed",
                "id": 257,
                "qty": 1
            },
            {
                "name": "Vial of water",
                "id": 227,
                "qty": 1
            }
        ]
    },
    {
        "name": "Snapdragon potion (unf)",
        "skill": "Herblore",
        "level": 59,
        "xp": 0.0,
        "output_id": 3004,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 2800,
        "materials": [
            {
                "name": "Clean snapdragon",
                "id": 3000,
                "qty": 1
            },
            {
                "name": "Vial of water",
                "id": 227,
                "qty": 1
            }
        ]
    },
    {
        "name": "Toadflax potion (unf)",
        "skill": "Herblore",
        "level": 30,
        "xp": 0.0,
        "output_id": 3002,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 2800,
        "materials": [
            {
                "name": "Clean toadflax",
                "id": 2998,
                "qty": 1
            },
            {
                "name": "Vial of water",
                "id": 227,
                "qty": 1
            }
        ]
    },
    {
        "name": "Torstol potion (unf)",
        "skill": "Herblore",
        "level": 75,
        "xp": 0.0,
        "output_id": 111,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 2800,
        "materials": [
            {
                "name": "Clean torstol",
                "id": 269,
                "qty": 1
            },
            {
                "name": "Vial of water",
                "id": 227,
                "qty": 1
            }
        ]
    },
    {
        "name": "Avantoe potion (unf)",
        "skill": "Herblore",
        "level": 48,
        "xp": 0.0,
        "output_id": 103,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 2800,
        "materials": [
            {
                "name": "Clean avantoe",
                "id": 261,
                "qty": 1
            },
            {
                "name": "Vial of water",
                "id": 227,
                "qty": 1
            }
        ]
    },
    {
        "name": "Kwuarm potion (unf)",
        "skill": "Herblore",
        "level": 54,
        "xp": 0.0,
        "output_id": 105,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 2800,
        "materials": [
            {
                "name": "Clean kwuarm",
                "id": 263,
                "qty": 1
            },
            {
                "name": "Vial of water",
                "id": 227,
                "qty": 1
            }
        ]
    },
    {
        "name": "Cadantine potion (unf)",
        "skill": "Herblore",
        "level": 65,
        "xp": 0.0,
        "output_id": 107,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 2800,
        "materials": [
            {
                "name": "Clean cadantine",
                "id": 265,
                "qty": 1
            },
            {
                "name": "Vial of water",
                "id": 227,
                "qty": 1
            }
        ]
    },
    {
        "name": "Clean ranarr weed",
        "skill": "Herblore",
        "level": 25,
        "xp": 7.5,
        "output_id": 257,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 4500,
        "materials": [
            {
                "name": "Grimy ranarr weed",
                "id": 207,
                "qty": 1
            }
        ]
    },
    {
        "name": "Clean snapdragon",
        "skill": "Herblore",
        "level": 59,
        "xp": 11.8,
        "output_id": 3000,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 4500,
        "materials": [
            {
                "name": "Grimy snapdragon",
                "id": 3051,
                "qty": 1
            }
        ]
    },
    {
        "name": "Clean torstol",
        "skill": "Herblore",
        "level": 75,
        "xp": 15.0,
        "output_id": 269,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 4500,
        "materials": [
            {
                "name": "Grimy torstol",
                "id": 219,
                "qty": 1
            }
        ]
    },
    {
        "name": "Clean avantoe",
        "skill": "Herblore",
        "level": 48,
        "xp": 10.0,
        "output_id": 261,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 4500,
        "materials": [
            {
                "name": "Grimy avantoe",
                "id": 211,
                "qty": 1
            }
        ]
    },
    {
        "name": "Clean kwuarm",
        "skill": "Herblore",
        "level": 54,
        "xp": 11.3,
        "output_id": 263,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 4500,
        "materials": [
            {
                "name": "Grimy kwuarm",
                "id": 213,
                "qty": 1
            }
        ]
    },
    {
        "name": "Clean cadantine",
        "skill": "Herblore",
        "level": 65,
        "xp": 12.5,
        "output_id": 265,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 4500,
        "materials": [
            {
                "name": "Grimy cadantine",
                "id": 215,
                "qty": 1
            }
        ]
    },
    {
        "name": "Clean toadflax",
        "skill": "Herblore",
        "level": 30,
        "xp": 8.0,
        "output_id": 2998,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 4500,
        "materials": [
            {
                "name": "Grimy toadflax",
                "id": 3049,
                "qty": 1
            }
        ]
    },
    {
        "name": "Crushed nest",
        "skill": "Herblore",
        "level": 1,
        "xp": 0.0,
        "output_id": 6693,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 3500,
        "materials": [
            {
                "name": "Bird nest",
                "id": 5075,
                "qty": 1
            }
        ]
    },
    {
        "name": "Dragon scale dust",
        "skill": "Herblore",
        "level": 1,
        "xp": 0.0,
        "output_id": 241,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 3500,
        "materials": [
            {
                "name": "Blue dragon scale",
                "id": 243,
                "qty": 1
            }
        ]
    },
    {
        "name": "Desert goat horn dust",
        "skill": "Herblore",
        "level": 1,
        "xp": 0.0,
        "output_id": 9736,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 3500,
        "materials": [
            {
                "name": "Desert goat horn",
                "id": 9735,
                "qty": 1
            }
        ]
    },
    {
        "name": "Chocolate dust",
        "skill": "Herblore",
        "level": 1,
        "xp": 0.0,
        "output_id": 1975,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 3500,
        "materials": [
            {
                "name": "Chocolate bar",
                "id": 1973,
                "qty": 1
            }
        ]
    },
    {
        "name": "Magic longbow",
        "skill": "Fletching",
        "level": 85,
        "xp": 91.5,
        "output_id": 859,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 1500,
        "materials": [
            {
                "name": "Magic longbow (u)",
                "id": 70,
                "qty": 1
            },
            {
                "name": "Bow string",
                "id": 1777,
                "qty": 1
            }
        ]
    },
    {
        "name": "Magic shortbow",
        "skill": "Fletching",
        "level": 80,
        "xp": 83.3,
        "output_id": 861,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 1500,
        "materials": [
            {
                "name": "Magic shortbow (u)",
                "id": 72,
                "qty": 1
            },
            {
                "name": "Bow string",
                "id": 1777,
                "qty": 1
            }
        ]
    },
    {
        "name": "Yew longbow",
        "skill": "Fletching",
        "level": 70,
        "xp": 75.0,
        "output_id": 855,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 1500,
        "materials": [
            {
                "name": "Yew longbow (u)",
                "id": 66,
                "qty": 1
            },
            {
                "name": "Bow string",
                "id": 1777,
                "qty": 1
            }
        ]
    },
    {
        "name": "Yew shortbow",
        "skill": "Fletching",
        "level": 65,
        "xp": 67.5,
        "output_id": 857,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 1500,
        "materials": [
            {
                "name": "Yew shortbow (u)",
                "id": 68,
                "qty": 1
            },
            {
                "name": "Bow string",
                "id": 1777,
                "qty": 1
            }
        ]
    },
    {
        "name": "Maple longbow",
        "skill": "Fletching",
        "level": 55,
        "xp": 58.3,
        "output_id": 851,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 1500,
        "materials": [
            {
                "name": "Maple longbow (u)",
                "id": 62,
                "qty": 1
            },
            {
                "name": "Bow string",
                "id": 1777,
                "qty": 1
            }
        ]
    },
    {
        "name": "Maple shortbow",
        "skill": "Fletching",
        "level": 50,
        "xp": 50.0,
        "output_id": 853,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 1500,
        "materials": [
            {
                "name": "Maple shortbow (u)",
                "id": 64,
                "qty": 1
            },
            {
                "name": "Bow string",
                "id": 1777,
                "qty": 1
            }
        ]
    },
    {
        "name": "Willow longbow",
        "skill": "Fletching",
        "level": 40,
        "xp": 41.5,
        "output_id": 847,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 1500,
        "materials": [
            {
                "name": "Willow longbow (u)",
                "id": 58,
                "qty": 1
            },
            {
                "name": "Bow string",
                "id": 1777,
                "qty": 1
            }
        ]
    },
    {
        "name": "Dragon dart (10x)",
        "skill": "Fletching",
        "level": 95,
        "xp": 250.0,
        "output_id": 11230,
        "output_qty": 10,
        "members": True,
        "hourly_actions": 15000,
        "materials": [
            {
                "name": "Dragon dart tip",
                "id": 11232,
                "qty": 10
            },
            {
                "name": "Feather",
                "id": 314,
                "qty": 10
            }
        ]
    },
    {
        "name": "Amethyst dart (10x)",
        "skill": "Fletching",
        "level": 90,
        "xp": 210.0,
        "output_id": 25849,
        "output_qty": 10,
        "members": True,
        "hourly_actions": 15000,
        "materials": [
            {
                "name": "Amethyst dart tip",
                "id": 25853,
                "qty": 10
            },
            {
                "name": "Feather",
                "id": 314,
                "qty": 10
            }
        ]
    },
    {
        "name": "Rune dart (10x)",
        "skill": "Fletching",
        "level": 74,
        "xp": 188.0,
        "output_id": 811,
        "output_qty": 10,
        "members": True,
        "hourly_actions": 15000,
        "materials": [
            {
                "name": "Rune dart tip",
                "id": 824,
                "qty": 10
            },
            {
                "name": "Feather",
                "id": 314,
                "qty": 10
            }
        ]
    },
    {
        "name": "Adamant dart (10x)",
        "skill": "Fletching",
        "level": 67,
        "xp": 150.0,
        "output_id": 810,
        "output_qty": 10,
        "members": True,
        "hourly_actions": 15000,
        "materials": [
            {
                "name": "Adamant dart tip",
                "id": 823,
                "qty": 10
            },
            {
                "name": "Feather",
                "id": 314,
                "qty": 10
            }
        ]
    },
    {
        "name": "Mithril dart (10x)",
        "skill": "Fletching",
        "level": 52,
        "xp": 112.0,
        "output_id": 809,
        "output_qty": 10,
        "members": True,
        "hourly_actions": 15000,
        "materials": [
            {
                "name": "Mithril dart tip",
                "id": 822,
                "qty": 10
            },
            {
                "name": "Feather",
                "id": 314,
                "qty": 10
            }
        ]
    },
    {
        "name": "Ruby bolts (10x)",
        "skill": "Fletching",
        "level": 63,
        "xp": 63.0,
        "output_id": 9339,
        "output_qty": 10,
        "members": True,
        "hourly_actions": 12000,
        "materials": [
            {
                "name": "Adamant bolts",
                "id": 9143,
                "qty": 10
            },
            {
                "name": "Ruby bolt tips",
                "id": 9191,
                "qty": 10
            }
        ]
    },
    {
        "name": "Diamond bolts (10x)",
        "skill": "Fletching",
        "level": 65,
        "xp": 70.0,
        "output_id": 9340,
        "output_qty": 10,
        "members": True,
        "hourly_actions": 12000,
        "materials": [
            {
                "name": "Adamant bolts",
                "id": 9143,
                "qty": 10
            },
            {
                "name": "Diamond bolt tips",
                "id": 9192,
                "qty": 10
            }
        ]
    },
    {
        "name": "Dragonstone bolts (10x)",
        "skill": "Fletching",
        "level": 82,
        "xp": 82.0,
        "output_id": 9341,
        "output_qty": 10,
        "members": True,
        "hourly_actions": 12000,
        "materials": [
            {
                "name": "Runite bolts",
                "id": 9144,
                "qty": 10
            },
            {
                "name": "Dragonstone bolt tips",
                "id": 9193,
                "qty": 10
            }
        ]
    },
    {
        "name": "Onyx bolts (10x)",
        "skill": "Fletching",
        "level": 73,
        "xp": 94.0,
        "output_id": 9342,
        "output_qty": 10,
        "members": True,
        "hourly_actions": 12000,
        "materials": [
            {
                "name": "Runite bolts",
                "id": 9144,
                "qty": 10
            },
            {
                "name": "Onyx bolt tips",
                "id": 9194,
                "qty": 10
            }
        ]
    },
    {
        "name": "Dragon crossbow",
        "skill": "Fletching",
        "level": 78,
        "xp": 70.0,
        "output_id": 21902,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 1400,
        "materials": [
            {
                "name": "Dragon crossbow (u)",
                "id": 21921,
                "qty": 1
            },
            {
                "name": "Crossbow string",
                "id": 9438,
                "qty": 1
            }
        ]
    },
    {
        "name": "Rune crossbow",
        "skill": "Fletching",
        "level": 69,
        "xp": 100.0,
        "output_id": 9185,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 1400,
        "materials": [
            {
                "name": "Runite crossbow (u)",
                "id": 9465,
                "qty": 1
            },
            {
                "name": "Crossbow string",
                "id": 9438,
                "qty": 1
            }
        ]
    },
    {
        "name": "Adamant crossbow",
        "skill": "Fletching",
        "level": 61,
        "xp": 82.0,
        "output_id": 9183,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 1400,
        "materials": [
            {
                "name": "Adamant crossbow (u)",
                "id": 9463,
                "qty": 1
            },
            {
                "name": "Crossbow string",
                "id": 9438,
                "qty": 1
            }
        ]
    },
    {
        "name": "Cannonball (4x)",
        "skill": "Smithing",
        "level": 35,
        "xp": 25.6,
        "output_id": 2,
        "output_qty": 4,
        "members": True,
        "hourly_actions": 2000,
        "materials": [
            {
                "name": "Steel bar",
                "id": 2353,
                "qty": 1
            }
        ]
    },
    {
        "name": "Rune dart tip (10x)",
        "skill": "Smithing",
        "level": 89,
        "xp": 75.0,
        "output_id": 824,
        "output_qty": 10,
        "members": True,
        "hourly_actions": 1000,
        "materials": [
            {
                "name": "Runite bar",
                "id": 2363,
                "qty": 1
            }
        ]
    },
    {
        "name": "Adamant dart tip (10x)",
        "skill": "Smithing",
        "level": 74,
        "xp": 62.5,
        "output_id": 823,
        "output_qty": 10,
        "members": True,
        "hourly_actions": 1000,
        "materials": [
            {
                "name": "Adamantite bar",
                "id": 2361,
                "qty": 1
            }
        ]
    },
    {
        "name": "Mithril dart tip (10x)",
        "skill": "Smithing",
        "level": 54,
        "xp": 50.0,
        "output_id": 822,
        "output_qty": 10,
        "members": True,
        "hourly_actions": 1000,
        "materials": [
            {
                "name": "Mithril bar",
                "id": 2359,
                "qty": 1
            }
        ]
    },
    {
        "name": "Runite bar (Blast Furnace)",
        "skill": "Smithing",
        "level": 85,
        "xp": 50.0,
        "output_id": 2363,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 2500,
        "materials": [
            {
                "name": "Runite ore",
                "id": 451,
                "qty": 1
            },
            {
                "name": "Coal",
                "id": 453,
                "qty": 4
            }
        ]
    },
    {
        "name": "Adamantite bar (Blast Furnace)",
        "skill": "Smithing",
        "level": 70,
        "xp": 37.5,
        "output_id": 2361,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 3000,
        "materials": [
            {
                "name": "Adamantite ore",
                "id": 449,
                "qty": 1
            },
            {
                "name": "Coal",
                "id": 453,
                "qty": 3
            }
        ]
    },
    {
        "name": "Mithril bar (Blast Furnace)",
        "skill": "Smithing",
        "level": 50,
        "xp": 30.0,
        "output_id": 2359,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 3500,
        "materials": [
            {
                "name": "Mithril ore",
                "id": 447,
                "qty": 1
            },
            {
                "name": "Coal",
                "id": 453,
                "qty": 2
            }
        ]
    },
    {
        "name": "Steel bar (Blast Furnace)",
        "skill": "Smithing",
        "level": 30,
        "xp": 17.5,
        "output_id": 2353,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 4000,
        "materials": [
            {
                "name": "Iron ore",
                "id": 440,
                "qty": 1
            },
            {
                "name": "Coal",
                "id": 453,
                "qty": 1
            }
        ]
    },
    {
        "name": "Gold bar (Blast Furnace)",
        "skill": "Smithing",
        "level": 40,
        "xp": 56.2,
        "output_id": 2357,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 5000,
        "materials": [
            {
                "name": "Gold ore",
                "id": 444,
                "qty": 1
            }
        ]
    },
    {
        "name": "Steel bar (Furnace)",
        "skill": "Smithing",
        "level": 30,
        "xp": 17.5,
        "output_id": 2353,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 1300,
        "materials": [
            {
                "name": "Iron ore",
                "id": 440,
                "qty": 1
            },
            {
                "name": "Coal",
                "id": 453,
                "qty": 2
            }
        ]
    },
    {
        "name": "Silver bar (Furnace)",
        "skill": "Smithing",
        "level": 20,
        "xp": 13.75,
        "output_id": 2355,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 1400,
        "materials": [
            {
                "name": "Silver ore",
                "id": 442,
                "qty": 1
            }
        ]
    },
    {
        "name": "Gold bar (Furnace)",
        "skill": "Smithing",
        "level": 40,
        "xp": 22.5,
        "output_id": 2357,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 1400,
        "materials": [
            {
                "name": "Gold ore",
                "id": 444,
                "qty": 1
            }
        ]
    },
    {
        "name": "Mithril bar (Furnace)",
        "skill": "Smithing",
        "level": 50,
        "xp": 30.0,
        "output_id": 2359,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 900,
        "materials": [
            {
                "name": "Mithril ore",
                "id": 447,
                "qty": 1
            },
            {
                "name": "Coal",
                "id": 453,
                "qty": 4
            }
        ]
    },
    {
        "name": "Adamantite bar (Furnace)",
        "skill": "Smithing",
        "level": 70,
        "xp": 37.5,
        "output_id": 2361,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 700,
        "materials": [
            {
                "name": "Adamantite ore",
                "id": 449,
                "qty": 1
            },
            {
                "name": "Coal",
                "id": 453,
                "qty": 6
            }
        ]
    },
    {
        "name": "Runite bar (Furnace)",
        "skill": "Smithing",
        "level": 85,
        "xp": 50.0,
        "output_id": 2363,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 500,
        "materials": [
            {
                "name": "Runite ore",
                "id": 451,
                "qty": 1
            },
            {
                "name": "Coal",
                "id": 453,
                "qty": 8
            }
        ]
    },
    {
        "name": "Bronze bar (Furnace)",
        "skill": "Smithing",
        "level": 1,
        "xp": 6.25,
        "output_id": 2349,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 1300,
        "materials": [
            {
                "name": "Copper ore",
                "id": 436,
                "qty": 1
            },
            {
                "name": "Tin ore",
                "id": 438,
                "qty": 1
            }
        ]
    },
    {
        "name": "Rune pickaxe",
        "skill": "Smithing",
        "level": 86,
        "xp": 75.0,
        "output_id": 1275,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 900,
        "materials": [
            {
                "name": "Runite bar",
                "id": 2363,
                "qty": 1
            }
        ]
    },
    {
        "name": "Rune scimitar",
        "skill": "Smithing",
        "level": 90,
        "xp": 150.0,
        "output_id": 1333,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 850,
        "materials": [
            {
                "name": "Runite bar",
                "id": 2363,
                "qty": 2
            }
        ]
    },
    {
        "name": "Rune 2h sword",
        "skill": "Smithing",
        "level": 99,
        "xp": 225.0,
        "output_id": 1319,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 800,
        "materials": [
            {
                "name": "Runite bar",
                "id": 2363,
                "qty": 3
            }
        ]
    },
    {
        "name": "Rune platebody",
        "skill": "Smithing",
        "level": 99,
        "xp": 375.0,
        "output_id": 1127,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 750,
        "materials": [
            {
                "name": "Runite bar",
                "id": 2363,
                "qty": 5
            }
        ]
    },
    {
        "name": "Rune platelegs",
        "skill": "Smithing",
        "level": 96,
        "xp": 225.0,
        "output_id": 1079,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 800,
        "materials": [
            {
                "name": "Runite bar",
                "id": 2363,
                "qty": 3
            }
        ]
    },
    {
        "name": "Adamant platebody",
        "skill": "Smithing",
        "level": 88,
        "xp": 312.5,
        "output_id": 1123,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 750,
        "materials": [
            {
                "name": "Adamantite bar",
                "id": 2361,
                "qty": 5
            }
        ]
    },
    {
        "name": "Adamant 2h sword",
        "skill": "Smithing",
        "level": 84,
        "xp": 187.5,
        "output_id": 1317,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 800,
        "materials": [
            {
                "name": "Adamantite bar",
                "id": 2361,
                "qty": 3
            }
        ]
    },
    {
        "name": "Adamant scimitar",
        "skill": "Smithing",
        "level": 80,
        "xp": 125.0,
        "output_id": 1331,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 850,
        "materials": [
            {
                "name": "Adamantite bar",
                "id": 2361,
                "qty": 2
            }
        ]
    },
    {
        "name": "Steel platebody",
        "skill": "Smithing",
        "level": 48,
        "xp": 187.5,
        "output_id": 1119,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 750,
        "materials": [
            {
                "name": "Steel bar",
                "id": 2353,
                "qty": 5
            }
        ]
    },
    {
        "name": "Steel 2h sword",
        "skill": "Smithing",
        "level": 44,
        "xp": 112.5,
        "output_id": 1311,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 800,
        "materials": [
            {
                "name": "Steel bar",
                "id": 2353,
                "qty": 3
            }
        ]
    },
    {
        "name": "Iron platebody",
        "skill": "Smithing",
        "level": 33,
        "xp": 125.0,
        "output_id": 1115,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 750,
        "materials": [
            {
                "name": "Iron bar",
                "id": 2351,
                "qty": 5
            }
        ]
    },
    {
        "name": "Bronze platebody",
        "skill": "Smithing",
        "level": 18,
        "xp": 62.5,
        "output_id": 1117,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 750,
        "materials": [
            {
                "name": "Bronze bar",
                "id": 2349,
                "qty": 5
            }
        ]
    },
    {
        "name": "Unpowered orb",
        "skill": "Crafting",
        "level": 46,
        "xp": 52.5,
        "output_id": 567,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 1800,
        "materials": [
            {
                "name": "Molten glass",
                "id": 1775,
                "qty": 1
            }
        ]
    },
    {
        "name": "Lantern lens",
        "skill": "Crafting",
        "level": 49,
        "xp": 55.0,
        "output_id": 4542,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 1800,
        "materials": [
            {
                "name": "Molten glass",
                "id": 1775,
                "qty": 1
            }
        ]
    },
    {
        "name": "Light orb",
        "skill": "Crafting",
        "level": 87,
        "xp": 70.0,
        "output_id": 10973,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 1800,
        "materials": [
            {
                "name": "Molten glass",
                "id": 1775,
                "qty": 1
            }
        ]
    },
    {
        "name": "Beer glass",
        "skill": "Crafting",
        "level": 1,
        "xp": 17.5,
        "output_id": 1919,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 1800,
        "materials": [
            {
                "name": "Molten glass",
                "id": 1775,
                "qty": 1
            }
        ]
    },
    {
        "name": "Vial",
        "skill": "Crafting",
        "level": 33,
        "xp": 35.0,
        "output_id": 229,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 1800,
        "materials": [
            {
                "name": "Molten glass",
                "id": 1775,
                "qty": 1
            }
        ]
    },
    {
        "name": "Cut Zenyte",
        "skill": "Crafting",
        "level": 89,
        "xp": 200.0,
        "output_id": 19493,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 3500,
        "materials": [
            {
                "name": "Uncut zenyte",
                "id": 19496,
                "qty": 1
            }
        ]
    },
    {
        "name": "Cut Onyx",
        "skill": "Crafting",
        "level": 67,
        "xp": 167.5,
        "output_id": 6573,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 3500,
        "materials": [
            {
                "name": "Uncut onyx",
                "id": 6571,
                "qty": 1
            }
        ]
    },
    {
        "name": "Cut Dragonstone",
        "skill": "Crafting",
        "level": 55,
        "xp": 137.5,
        "output_id": 1613,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 3500,
        "materials": [
            {
                "name": "Uncut dragonstone",
                "id": 1615,
                "qty": 1
            }
        ]
    },
    {
        "name": "Cut Diamond",
        "skill": "Crafting",
        "level": 43,
        "xp": 107.5,
        "output_id": 1601,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 3500,
        "materials": [
            {
                "name": "Uncut diamond",
                "id": 1617,
                "qty": 1
            }
        ]
    },
    {
        "name": "Cut Ruby",
        "skill": "Crafting",
        "level": 34,
        "xp": 85.0,
        "output_id": 1603,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 3500,
        "materials": [
            {
                "name": "Uncut ruby",
                "id": 1619,
                "qty": 1
            }
        ]
    },
    {
        "name": "Cut Emerald",
        "skill": "Crafting",
        "level": 27,
        "xp": 67.5,
        "output_id": 1605,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 3500,
        "materials": [
            {
                "name": "Uncut emerald",
                "id": 1621,
                "qty": 1
            }
        ]
    },
    {
        "name": "Cut Sapphire",
        "skill": "Crafting",
        "level": 20,
        "xp": 50.0,
        "output_id": 1607,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 3500,
        "materials": [
            {
                "name": "Uncut sapphire",
                "id": 1623,
                "qty": 1
            }
        ]
    },
    {
        "name": "Air battlestaff",
        "skill": "Crafting",
        "level": 66,
        "xp": 137.5,
        "output_id": 1397,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 2300,
        "materials": [
            {
                "name": "Battlestaff",
                "id": 1391,
                "qty": 1
            },
            {
                "name": "Air orb",
                "id": 573,
                "qty": 1
            }
        ]
    },
    {
        "name": "Fire battlestaff",
        "skill": "Crafting",
        "level": 62,
        "xp": 125.0,
        "output_id": 1393,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 2300,
        "materials": [
            {
                "name": "Battlestaff",
                "id": 1391,
                "qty": 1
            },
            {
                "name": "Fire orb",
                "id": 569,
                "qty": 1
            }
        ]
    },
    {
        "name": "Water battlestaff",
        "skill": "Crafting",
        "level": 54,
        "xp": 100.0,
        "output_id": 1395,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 2300,
        "materials": [
            {
                "name": "Battlestaff",
                "id": 1391,
                "qty": 1
            },
            {
                "name": "Water orb",
                "id": 571,
                "qty": 1
            }
        ]
    },
    {
        "name": "Earth battlestaff",
        "skill": "Crafting",
        "level": 58,
        "xp": 112.5,
        "output_id": 1399,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 2300,
        "materials": [
            {
                "name": "Battlestaff",
                "id": 1391,
                "qty": 1
            },
            {
                "name": "Earth orb",
                "id": 575,
                "qty": 1
            }
        ]
    },
    {
        "name": "Black d'hide body",
        "skill": "Crafting",
        "level": 84,
        "xp": 258.0,
        "output_id": 2503,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 1200,
        "materials": [
            {
                "name": "Black dragon leather",
                "id": 2509,
                "qty": 3
            },
            {
                "name": "Thread",
                "id": 1734,
                "qty": 1
            }
        ]
    },
    {
        "name": "Black d'hide chaps",
        "skill": "Crafting",
        "level": 82,
        "xp": 172.0,
        "output_id": 2497,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 1200,
        "materials": [
            {
                "name": "Black dragon leather",
                "id": 2509,
                "qty": 2
            },
            {
                "name": "Thread",
                "id": 1734,
                "qty": 1
            }
        ]
    },
    {
        "name": "Red d'hide body",
        "skill": "Crafting",
        "level": 77,
        "xp": 234.0,
        "output_id": 2499,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 1200,
        "materials": [
            {
                "name": "Red dragon leather",
                "id": 2507,
                "qty": 3
            },
            {
                "name": "Thread",
                "id": 1734,
                "qty": 1
            }
        ]
    },
    {
        "name": "Blue d'hide body",
        "skill": "Crafting",
        "level": 71,
        "xp": 210.0,
        "output_id": 2493,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 1200,
        "materials": [
            {
                "name": "Blue dragon leather",
                "id": 2505,
                "qty": 3
            },
            {
                "name": "Thread",
                "id": 1734,
                "qty": 1
            }
        ]
    },
    {
        "name": "Green d'hide body",
        "skill": "Crafting",
        "level": 63,
        "xp": 186.0,
        "output_id": 1135,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 1200,
        "materials": [
            {
                "name": "Green dragon leather",
                "id": 1745,
                "qty": 3
            },
            {
                "name": "Thread",
                "id": 1734,
                "qty": 1
            }
        ]
    },
    {
        "name": "Diamond amulet (u)",
        "skill": "Crafting",
        "level": 70,
        "xp": 100.0,
        "output_id": 1681,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 1400,
        "materials": [
            {
                "name": "Gold bar",
                "id": 2357,
                "qty": 1
            },
            {
                "name": "Diamond",
                "id": 1601,
                "qty": 1
            }
        ]
    },
    {
        "name": "Ruby amulet (u)",
        "skill": "Crafting",
        "level": 50,
        "xp": 85.0,
        "output_id": 1679,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 1400,
        "materials": [
            {
                "name": "Gold bar",
                "id": 2357,
                "qty": 1
            },
            {
                "name": "Ruby",
                "id": 1603,
                "qty": 1
            }
        ]
    },
    {
        "name": "Emerald ring",
        "skill": "Crafting",
        "level": 27,
        "xp": 55.0,
        "output_id": 1639,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 1400,
        "materials": [
            {
                "name": "Gold bar",
                "id": 2357,
                "qty": 1
            },
            {
                "name": "Emerald",
                "id": 1605,
                "qty": 1
            }
        ]
    },
    {
        "name": "Sapphire ring",
        "skill": "Crafting",
        "level": 20,
        "xp": 40.0,
        "output_id": 1637,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 1400,
        "materials": [
            {
                "name": "Gold bar",
                "id": 2357,
                "qty": 1
            },
            {
                "name": "Sapphire",
                "id": 1607,
                "qty": 1
            }
        ]
    },
    {
        "name": "Gold ring",
        "skill": "Crafting",
        "level": 5,
        "xp": 15.0,
        "output_id": 1635,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 1400,
        "materials": [
            {
                "name": "Gold bar",
                "id": 2357,
                "qty": 1
            }
        ]
    },
    {
        "name": "Bow string (Spinning)",
        "skill": "Crafting",
        "level": 10,
        "xp": 15.0,
        "output_id": 1777,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 1400,
        "materials": [
            {
                "name": "Flax",
                "id": 1779,
                "qty": 1
            }
        ]
    },
    {
        "name": "Cooked shark",
        "skill": "Cooking",
        "level": 80,
        "xp": 210.0,
        "output_id": 385,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 1300,
        "materials": [
            {
                "name": "Raw shark",
                "id": 383,
                "qty": 1
            }
        ]
    },
    {
        "name": "Cooked karambwan",
        "skill": "Cooking",
        "level": 30,
        "xp": 190.0,
        "output_id": 3144,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 4000,
        "materials": [
            {
                "name": "Raw karambwan",
                "id": 3142,
                "qty": 1
            }
        ]
    },
    {
        "name": "Cooked anglerfish",
        "skill": "Cooking",
        "level": 84,
        "xp": 230.0,
        "output_id": 13441,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 1300,
        "materials": [
            {
                "name": "Raw anglerfish",
                "id": 13439,
                "qty": 1
            }
        ]
    },
    {
        "name": "Cooked monkfish",
        "skill": "Cooking",
        "level": 62,
        "xp": 150.0,
        "output_id": 7946,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 1300,
        "materials": [
            {
                "name": "Raw monkfish",
                "id": 7944,
                "qty": 1
            }
        ]
    },
    {
        "name": "Cooked manta ray",
        "skill": "Cooking",
        "level": 91,
        "xp": 216.0,
        "output_id": 391,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 1300,
        "materials": [
            {
                "name": "Raw manta ray",
                "id": 389,
                "qty": 1
            }
        ]
    },
    {
        "name": "Cooked swordfish",
        "skill": "Cooking",
        "level": 45,
        "xp": 140.0,
        "output_id": 373,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 1300,
        "materials": [
            {
                "name": "Raw swordfish",
                "id": 371,
                "qty": 1
            }
        ]
    },
    {
        "name": "Cooked lobster",
        "skill": "Cooking",
        "level": 40,
        "xp": 120.0,
        "output_id": 379,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 1300,
        "materials": [
            {
                "name": "Raw lobster",
                "id": 377,
                "qty": 1
            }
        ]
    },
    {
        "name": "Jug of wine",
        "skill": "Cooking",
        "level": 35,
        "xp": 200.0,
        "output_id": 1993,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 2500,
        "materials": [
            {
                "name": "Grapes",
                "id": 1987,
                "qty": 1
            },
            {
                "name": "Jug of water",
                "id": 1937,
                "qty": 1
            }
        ]
    },
    {
        "name": "Ring of recoil",
        "skill": "Magic",
        "level": 7,
        "xp": 17.5,
        "output_id": 2550,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 2000,
        "materials": [
            {
                "name": "Sapphire ring",
                "id": 1637,
                "qty": 1
            },
            {
                "name": "Cosmic rune",
                "id": 564,
                "qty": 1
            },
            {
                "name": "Water rune",
                "id": 555,
                "qty": 1
            }
        ]
    },
    {
        "name": "Games necklace(8)",
        "skill": "Magic",
        "level": 7,
        "xp": 17.5,
        "output_id": 3853,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 2000,
        "materials": [
            {
                "name": "Sapphire necklace",
                "id": 1656,
                "qty": 1
            },
            {
                "name": "Cosmic rune",
                "id": 564,
                "qty": 1
            },
            {
                "name": "Water rune",
                "id": 555,
                "qty": 1
            }
        ]
    },
    {
        "name": "Ring of dueling(8)",
        "skill": "Magic",
        "level": 27,
        "xp": 37.0,
        "output_id": 2552,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 2000,
        "materials": [
            {
                "name": "Emerald ring",
                "id": 1639,
                "qty": 1
            },
            {
                "name": "Cosmic rune",
                "id": 564,
                "qty": 1
            },
            {
                "name": "Air rune",
                "id": 556,
                "qty": 3
            }
        ]
    },
    {
        "name": "Combat bracelet(4)",
        "skill": "Magic",
        "level": 68,
        "xp": 78.0,
        "output_id": 11126,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 2000,
        "materials": [
            {
                "name": "Dragonstone bracelet",
                "id": 11118,
                "qty": 1
            },
            {
                "name": "Cosmic rune",
                "id": 564,
                "qty": 1
            },
            {
                "name": "Earth rune",
                "id": 557,
                "qty": 15
            },
            {
                "name": "Water rune",
                "id": 555,
                "qty": 15
            }
        ]
    },
    {
        "name": "Skills necklace(4)",
        "skill": "Magic",
        "level": 68,
        "xp": 78.0,
        "output_id": 11105,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 2000,
        "materials": [
            {
                "name": "Dragonstone necklace",
                "id": 1664,
                "qty": 1
            },
            {
                "name": "Cosmic rune",
                "id": 564,
                "qty": 1
            },
            {
                "name": "Earth rune",
                "id": 557,
                "qty": 15
            },
            {
                "name": "Water rune",
                "id": 555,
                "qty": 15
            }
        ]
    },
    {
        "name": "Amulet of fury",
        "skill": "Magic",
        "level": 87,
        "xp": 110.0,
        "output_id": 6585,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 2000,
        "materials": [
            {
                "name": "Onyx amulet",
                "id": 6581,
                "qty": 1
            },
            {
                "name": "Cosmic rune",
                "id": 564,
                "qty": 1
            },
            {
                "name": "Earth rune",
                "id": 557,
                "qty": 20
            },
            {
                "name": "Fire rune",
                "id": 554,
                "qty": 20
            }
        ]
    },
    {
        "name": "Ring of suffering",
        "skill": "Magic",
        "level": 93,
        "xp": 110.0,
        "output_id": 19550,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 2000,
        "materials": [
            {
                "name": "Zenyte ring",
                "id": 19538,
                "qty": 1
            },
            {
                "name": "Cosmic rune",
                "id": 564,
                "qty": 1
            },
            {
                "name": "Soul rune",
                "id": 566,
                "qty": 20
            },
            {
                "name": "Blood rune",
                "id": 565,
                "qty": 20
            }
        ]
    },
    {
        "name": "Amulet of torture",
        "skill": "Magic",
        "level": 93,
        "xp": 110.0,
        "output_id": 19553,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 2000,
        "materials": [
            {
                "name": "Zenyte amulet",
                "id": 19541,
                "qty": 1
            },
            {
                "name": "Cosmic rune",
                "id": 564,
                "qty": 1
            },
            {
                "name": "Soul rune",
                "id": 566,
                "qty": 20
            },
            {
                "name": "Blood rune",
                "id": 565,
                "qty": 20
            }
        ]
    },
    {
        "name": "Necklace of anguish",
        "skill": "Magic",
        "level": 93,
        "xp": 110.0,
        "output_id": 19547,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 2000,
        "materials": [
            {
                "name": "Zenyte necklace",
                "id": 19535,
                "qty": 1
            },
            {
                "name": "Cosmic rune",
                "id": 564,
                "qty": 1
            },
            {
                "name": "Soul rune",
                "id": 566,
                "qty": 20
            },
            {
                "name": "Blood rune",
                "id": 565,
                "qty": 20
            }
        ]
    },
    {
        "name": "Tormented bracelet",
        "skill": "Magic",
        "level": 93,
        "xp": 110.0,
        "output_id": 19544,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 2000,
        "materials": [
            {
                "name": "Zenyte bracelet",
                "id": 19532,
                "qty": 1
            },
            {
                "name": "Cosmic rune",
                "id": 564,
                "qty": 1
            },
            {
                "name": "Soul rune",
                "id": 566,
                "qty": 20
            },
            {
                "name": "Blood rune",
                "id": 565,
                "qty": 20
            }
        ]
    },
    {
        "name": "Onyx bolts (e) (10x)",
        "skill": "Magic",
        "level": 87,
        "xp": 97.0,
        "output_id": 9245,
        "output_qty": 10,
        "members": True,
        "hourly_actions": 12000,
        "materials": [
            {
                "name": "Onyx bolts",
                "id": 9342,
                "qty": 10
            },
            {
                "name": "Cosmic rune",
                "id": 564,
                "qty": 1
            },
            {
                "name": "Death rune",
                "id": 560,
                "qty": 1
            },
            {
                "name": "Fire rune",
                "id": 554,
                "qty": 1
            }
        ]
    },
    {
        "name": "Dragonstone bolts (e) (10x)",
        "skill": "Magic",
        "level": 68,
        "xp": 78.0,
        "output_id": 9244,
        "output_qty": 10,
        "members": True,
        "hourly_actions": 12000,
        "materials": [
            {
                "name": "Dragonstone bolts",
                "id": 9341,
                "qty": 10
            },
            {
                "name": "Cosmic rune",
                "id": 564,
                "qty": 1
            },
            {
                "name": "Soul rune",
                "id": 566,
                "qty": 2
            },
            {
                "name": "Earth rune",
                "id": 557,
                "qty": 2
            }
        ]
    },
    {
        "name": "Diamond bolts (e) (10x)",
        "skill": "Magic",
        "level": 57,
        "xp": 67.0,
        "output_id": 9243,
        "output_qty": 10,
        "members": True,
        "hourly_actions": 12000,
        "materials": [
            {
                "name": "Diamond bolts",
                "id": 9340,
                "qty": 10
            },
            {
                "name": "Cosmic rune",
                "id": 564,
                "qty": 1
            },
            {
                "name": "Law rune",
                "id": 563,
                "qty": 2
            },
            {
                "name": "Earth rune",
                "id": 557,
                "qty": 1
            }
        ]
    },
    {
        "name": "Ruby bolts (e) (10x)",
        "skill": "Magic",
        "level": 49,
        "xp": 59.0,
        "output_id": 9242,
        "output_qty": 10,
        "members": True,
        "hourly_actions": 12000,
        "materials": [
            {
                "name": "Ruby bolts",
                "id": 9339,
                "qty": 10
            },
            {
                "name": "Cosmic rune",
                "id": 564,
                "qty": 1
            },
            {
                "name": "Blood rune",
                "id": 565,
                "qty": 1
            },
            {
                "name": "Fire rune",
                "id": 554,
                "qty": 5
            }
        ]
    },
    {
        "name": "Mahogany plank (Plank Make)",
        "skill": "Magic",
        "level": 86,
        "xp": 90.0,
        "output_id": 8782,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 1400,
        "materials": [
            {
                "name": "Mahogany logs",
                "id": 6332,
                "qty": 1
            },
            {
                "name": "Astral rune",
                "id": 9075,
                "qty": 2
            },
            {
                "name": "Nature rune",
                "id": 561,
                "qty": 1
            }
        ]
    },
    {
        "name": "Teak plank (Plank Make)",
        "skill": "Magic",
        "level": 86,
        "xp": 90.0,
        "output_id": 8780,
        "output_qty": 1,
        "members": True,
        "hourly_actions": 1400,
        "materials": [
            {
                "name": "Teak logs",
                "id": 6333,
                "qty": 1
            },
            {
                "name": "Astral rune",
                "id": 9075,
                "qty": 2
            },
            {
                "name": "Nature rune",
                "id": 561,
                "qty": 1
            }
        ]
    },
    {
        "name": "Rune arrowtips (15x)",
        "skill": "Smithing",
        "level": 90,
        "xp": 75.0,
        "output_id": 44,
        "output_qty": 15,
        "members": True,
        "hourly_actions": 950,
        "materials": [
            {
                "name": "Runite bar",
                "id": 2363,
                "qty": 1
            }
        ]
    },
    {
        "name": "Runite bolts (unf) (10x)",
        "skill": "Smithing",
        "level": 88,
        "xp": 75.0,
        "output_id": 9381,
        "output_qty": 10,
        "members": True,
        "hourly_actions": 950,
        "materials": [
            {
                "name": "Runite bar",
                "id": 2363,
                "qty": 1
            }
        ]
    },
    {
        "name": "Rune knife (5x)",
        "skill": "Smithing",
        "level": 92,
        "xp": 75.0,
        "output_id": 868,
        "output_qty": 5,
        "members": True,
        "hourly_actions": 900,
        "materials": [
            {
                "name": "Runite bar",
                "id": 2363,
                "qty": 1
            }
        ]
    },
    {
        "name": "Rune cannonball (4x)",
        "skill": "Smithing",
        "level": 90,
        "xp": 50.5,
        "output_id": 31914,
        "output_qty": 4,
        "members": True,
        "hourly_actions": 800,
        "materials": [
            {
                "name": "Runite bar",
                "id": 2363,
                "qty": 1
            }
        ]
    },
    {
        "name": "Rune sword",
        "skill": "Smithing",
        "level": 89,
        "xp": 75.0,
        "output_id": 1289,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 900,
        "materials": [
            {
                "name": "Runite bar",
                "id": 2363,
                "qty": 1
            }
        ]
    },
    {
        "name": "Rune med helm",
        "skill": "Smithing",
        "level": 88,
        "xp": 75.0,
        "output_id": 1147,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 900,
        "materials": [
            {
                "name": "Runite bar",
                "id": 2363,
                "qty": 1
            }
        ]
    },
    {
        "name": "Rune full helm",
        "skill": "Smithing",
        "level": 92,
        "xp": 150.0,
        "output_id": 1163,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 850,
        "materials": [
            {
                "name": "Runite bar",
                "id": 2363,
                "qty": 2
            }
        ]
    },
    {
        "name": "Rune sq shield",
        "skill": "Smithing",
        "level": 93,
        "xp": 150.0,
        "output_id": 1185,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 850,
        "materials": [
            {
                "name": "Runite bar",
                "id": 2363,
                "qty": 2
            }
        ]
    },
    {
        "name": "Rune warhammer",
        "skill": "Smithing",
        "level": 94,
        "xp": 225.0,
        "output_id": 1347,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 800,
        "materials": [
            {
                "name": "Runite bar",
                "id": 2363,
                "qty": 3
            }
        ]
    },
    {
        "name": "Rune battleaxe",
        "skill": "Smithing",
        "level": 95,
        "xp": 225.0,
        "output_id": 1373,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 800,
        "materials": [
            {
                "name": "Runite bar",
                "id": 2363,
                "qty": 3
            }
        ]
    },
    {
        "name": "Rune chainbody",
        "skill": "Smithing",
        "level": 96,
        "xp": 225.0,
        "output_id": 1113,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 800,
        "materials": [
            {
                "name": "Runite bar",
                "id": 2363,
                "qty": 3
            }
        ]
    },
    {
        "name": "Rune kiteshield",
        "skill": "Smithing",
        "level": 97,
        "xp": 225.0,
        "output_id": 1201,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 800,
        "materials": [
            {
                "name": "Runite bar",
                "id": 2363,
                "qty": 3
            }
        ]
    },
    {
        "name": "Rune plateskirt",
        "skill": "Smithing",
        "level": 99,
        "xp": 225.0,
        "output_id": 1093,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 800,
        "materials": [
            {
                "name": "Runite bar",
                "id": 2363,
                "qty": 3
            }
        ]
    },
    {
        "name": "Adamant arrowtips (15x)",
        "skill": "Smithing",
        "level": 75,
        "xp": 62.5,
        "output_id": 43,
        "output_qty": 15,
        "members": True,
        "hourly_actions": 950,
        "materials": [
            {
                "name": "Adamantite bar",
                "id": 2361,
                "qty": 1
            }
        ]
    },
    {
        "name": "Adamant bolts(unf) (10x)",
        "skill": "Smithing",
        "level": 73,
        "xp": 62.5,
        "output_id": 9380,
        "output_qty": 10,
        "members": True,
        "hourly_actions": 950,
        "materials": [
            {
                "name": "Adamantite bar",
                "id": 2361,
                "qty": 1
            }
        ]
    },
    {
        "name": "Adamant knife (5x)",
        "skill": "Smithing",
        "level": 77,
        "xp": 62.5,
        "output_id": 867,
        "output_qty": 5,
        "members": True,
        "hourly_actions": 900,
        "materials": [
            {
                "name": "Adamantite bar",
                "id": 2361,
                "qty": 1
            }
        ]
    },
    {
        "name": "Adamant warhammer",
        "skill": "Smithing",
        "level": 79,
        "xp": 187.5,
        "output_id": 1345,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 800,
        "materials": [
            {
                "name": "Adamantite bar",
                "id": 2361,
                "qty": 3
            }
        ]
    },
    {
        "name": "Adamant battleaxe",
        "skill": "Smithing",
        "level": 80,
        "xp": 187.5,
        "output_id": 1371,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 800,
        "materials": [
            {
                "name": "Adamantite bar",
                "id": 2361,
                "qty": 3
            }
        ]
    },
    {
        "name": "Adamant chainbody",
        "skill": "Smithing",
        "level": 81,
        "xp": 187.5,
        "output_id": 1111,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 800,
        "materials": [
            {
                "name": "Adamantite bar",
                "id": 2361,
                "qty": 3
            }
        ]
    },
    {
        "name": "Adamant kiteshield",
        "skill": "Smithing",
        "level": 82,
        "xp": 187.5,
        "output_id": 1199,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 800,
        "materials": [
            {
                "name": "Adamantite bar",
                "id": 2361,
                "qty": 3
            }
        ]
    },
    {
        "name": "Adamant platelegs",
        "skill": "Smithing",
        "level": 86,
        "xp": 187.5,
        "output_id": 1073,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 800,
        "materials": [
            {
                "name": "Adamantite bar",
                "id": 2361,
                "qty": 3
            }
        ]
    },
    {
        "name": "Adamant plateskirt",
        "skill": "Smithing",
        "level": 86,
        "xp": 187.5,
        "output_id": 1091,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 800,
        "materials": [
            {
                "name": "Adamantite bar",
                "id": 2361,
                "qty": 3
            }
        ]
    },
    {
        "name": "Mithril arrowtips (15x)",
        "skill": "Smithing",
        "level": 55,
        "xp": 50.0,
        "output_id": 42,
        "output_qty": 15,
        "members": True,
        "hourly_actions": 950,
        "materials": [
            {
                "name": "Mithril bar",
                "id": 2359,
                "qty": 1
            }
        ]
    },
    {
        "name": "Mithril bolts (unf) (10x)",
        "skill": "Smithing",
        "level": 53,
        "xp": 50.0,
        "output_id": 9379,
        "output_qty": 10,
        "members": True,
        "hourly_actions": 950,
        "materials": [
            {
                "name": "Mithril bar",
                "id": 2359,
                "qty": 1
            }
        ]
    },
    {
        "name": "Mithril knife (5x)",
        "skill": "Smithing",
        "level": 57,
        "xp": 50.0,
        "output_id": 866,
        "output_qty": 5,
        "members": True,
        "hourly_actions": 900,
        "materials": [
            {
                "name": "Mithril bar",
                "id": 2359,
                "qty": 1
            }
        ]
    },
    {
        "name": "Mithril scimitar",
        "skill": "Smithing",
        "level": 55,
        "xp": 100.0,
        "output_id": 1329,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 850,
        "materials": [
            {
                "name": "Mithril bar",
                "id": 2359,
                "qty": 2
            }
        ]
    },
    {
        "name": "Mithril 2h sword",
        "skill": "Smithing",
        "level": 64,
        "xp": 150.0,
        "output_id": 1315,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 800,
        "materials": [
            {
                "name": "Mithril bar",
                "id": 2359,
                "qty": 3
            }
        ]
    },
    {
        "name": "Mithril platelegs",
        "skill": "Smithing",
        "level": 66,
        "xp": 150.0,
        "output_id": 1071,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 800,
        "materials": [
            {
                "name": "Mithril bar",
                "id": 2359,
                "qty": 3
            }
        ]
    },
    {
        "name": "Mithril plateskirt",
        "skill": "Smithing",
        "level": 66,
        "xp": 150.0,
        "output_id": 1085,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 800,
        "materials": [
            {
                "name": "Mithril bar",
                "id": 2359,
                "qty": 3
            }
        ]
    },
    {
        "name": "Steel arrowtips (15x)",
        "skill": "Smithing",
        "level": 35,
        "xp": 37.5,
        "output_id": 41,
        "output_qty": 15,
        "members": True,
        "hourly_actions": 950,
        "materials": [
            {
                "name": "Steel bar",
                "id": 2353,
                "qty": 1
            }
        ]
    },
    {
        "name": "Steel bolts (unf) (10x)",
        "skill": "Smithing",
        "level": 33,
        "xp": 37.5,
        "output_id": 9378,
        "output_qty": 10,
        "members": True,
        "hourly_actions": 950,
        "materials": [
            {
                "name": "Steel bar",
                "id": 2353,
                "qty": 1
            }
        ]
    },
    {
        "name": "Steel knife (5x)",
        "skill": "Smithing",
        "level": 37,
        "xp": 37.5,
        "output_id": 865,
        "output_qty": 5,
        "members": True,
        "hourly_actions": 900,
        "materials": [
            {
                "name": "Steel bar",
                "id": 2353,
                "qty": 1
            }
        ]
    },
    {
        "name": "Steel scimitar",
        "skill": "Smithing",
        "level": 35,
        "xp": 75.0,
        "output_id": 1325,
        "output_qty": 1,
        "members": False,
        "hourly_actions": 850,
        "materials": [
            {
                "name": "Steel bar",
                "id": 2353,
                "qty": 2
            }
        ]
    },
    {
        "name": "Steel dart (10x)",
        "skill": "Fletching",
        "level": 34,
        "xp": 75.0,
        "output_id": 808,
        "output_qty": 10,
        "members": True,
        "hourly_actions": 2500,
        "materials": [
            {
                "name": "Steel dart tip",
                "id": 821,
                "qty": 10
            },
            {
                "name": "Feather",
                "id": 314,
                "qty": 10
            }
        ]
    },
    {
        "name": "Amethyst bolt tips (8x)",
        "skill": "Crafting",
        "level": 83,
        "xp": 60.0,
        "output_id": 21338,
        "output_qty": 8,
        "members": True,
        "hourly_actions": 1200,
        "materials": [
            {
                "name": "Amethyst",
                "id": 21347,
                "qty": 1
            }
        ]
    },
    {
        "name": "Amethyst arrowtips (15x)",
        "skill": "Crafting",
        "level": 85,
        "xp": 60.0,
        "output_id": 21332,
        "output_qty": 15,
        "members": True,
        "hourly_actions": 1200,
        "materials": [
            {
                "name": "Amethyst",
                "id": 21347,
                "qty": 1
            }
        ]
    },
    {
        "name": "Amethyst dart tips (8x)",
        "skill": "Crafting",
        "level": 89,
        "xp": 60.0,
        "output_id": 25853,
        "output_qty": 8,
        "members": True,
        "hourly_actions": 1200,
        "materials": [
            {
                "name": "Amethyst",
                "id": 21347,
                "qty": 1
            }
        ]
    },
{
    "name": "Antipoison(3)",
    "skill": "Herblore",
    "level": 5,
    "xp": 37.5,
    "output_id": 175,
    "output_qty": 1,
    "members": True,
    "hourly_actions": 2200,
    "materials": [
        {
            "name": "Marrentill potion (unf)",
            "id": 93,
            "qty": 1
        },
        {
            "name": "Ground unicorn horn",
            "id": 235,
            "qty": 1
        }
    ]
},
{
    "name": "Super energy(3)",
    "skill": "Herblore",
    "level": 52,
    "xp": 117.5,
    "output_id": 3018,
    "output_qty": 1,
    "members": True,
    "hourly_actions": 2200,
    "materials": [
        {
            "name": "Avantoe potion (unf)",
            "id": 103,
            "qty": 1
        },
        {
            "name": "Mort myre fungus",
            "id": 2970,
            "qty": 1
        }
    ]
},
{
    "name": "Zamorak brew(3)",
    "skill": "Herblore",
    "level": 78,
    "xp": 175.0,
    "output_id": 189,
    "output_qty": 1,
    "members": True,
    "hourly_actions": 2200,
    "materials": [
        {
            "name": "Torstol potion (unf)",
            "id": 111,
            "qty": 1
        },
        {
            "name": "Jangerberries",
            "id": 247,
            "qty": 1
        }
    ]
},
{
    "name": "Anti-venom(4)",
    "skill": "Herblore",
    "level": 87,
    "xp": 120.0,
    "output_id": 12905,
    "output_qty": 1,
    "members": True,
    "hourly_actions": 2200,
    "materials": [
        {
            "name": "Antidote++(4)",
            "id": 5952,
            "qty": 1
        },
        {
            "name": "Zulrah's scales",
            "id": 12934,
            "qty": 5
        }
    ]
},
{
    "name": "Anti-venom+(4)",
    "skill": "Herblore",
    "level": 94,
    "xp": 125.0,
    "output_id": 12913,
    "output_qty": 1,
    "members": True,
    "hourly_actions": 2200,
    "materials": [
        {
            "name": "Anti-venom(4)",
            "id": 12905,
            "qty": 1
        },
        {
            "name": "Torstol",
            "id": 269,
            "qty": 1
        }
    ]
},
{
    "name": "Super antifire potion(4)",
    "skill": "Herblore",
    "level": 92,
    "xp": 130.0,
    "output_id": 21978,
    "output_qty": 1,
    "members": True,
    "hourly_actions": 2200,
    "materials": [
        {
            "name": "Antifire potion(4)",
            "id": 2452,
            "qty": 1
        },
        {
            "name": "Crushed superior dragon bones",
            "id": 21975,
            "qty": 1
        }
    ]
},
{
    "name": "Extended super antifire(4)",
    "skill": "Herblore",
    "level": 98,
    "xp": 160.0,
    "output_id": 22209,
    "output_qty": 1,
    "members": True,
    "hourly_actions": 2200,
    "materials": [
        {
            "name": "Super antifire potion(4)",
            "id": 21978,
            "qty": 1
        },
        {
            "name": "Lava scale shard",
            "id": 11994,
            "qty": 4
        }
    ]
},
{
    "name": "Clean Guam leaf",
    "skill": "Herblore",
    "level": 3,
    "xp": 2.5,
    "output_id": 249,
    "output_qty": 1,
    "members": True,
    "hourly_actions": 3500,
    "materials": [
        {
            "name": "Grimy guam leaf",
            "id": 199,
            "qty": 1
        }
    ]
},
{
    "name": "Guam potion (unf)",
    "skill": "Herblore",
    "level": 3,
    "xp": 0.0,
    "output_id": 91,
    "output_qty": 1,
    "members": True,
    "hourly_actions": 2500,
    "materials": [
        {
            "name": "Guam leaf",
            "id": 249,
            "qty": 1
        },
        {
            "name": "Vial of water",
            "id": 227,
            "qty": 1
        }
    ]
},
{
    "name": "Clean Marrentill",
    "skill": "Herblore",
    "level": 5,
    "xp": 3.8,
    "output_id": 251,
    "output_qty": 1,
    "members": True,
    "hourly_actions": 3500,
    "materials": [
        {
            "name": "Grimy marrentill",
            "id": 201,
            "qty": 1
        }
    ]
},
{
    "name": "Marrentill potion (unf)",
    "skill": "Herblore",
    "level": 5,
    "xp": 0.0,
    "output_id": 93,
    "output_qty": 1,
    "members": True,
    "hourly_actions": 2500,
    "materials": [
        {
            "name": "Marrentill",
            "id": 251,
            "qty": 1
        },
        {
            "name": "Vial of water",
            "id": 227,
            "qty": 1
        }
    ]
},
{
    "name": "Clean Tarromin",
    "skill": "Herblore",
    "level": 11,
    "xp": 5.0,
    "output_id": 253,
    "output_qty": 1,
    "members": True,
    "hourly_actions": 3500,
    "materials": [
        {
            "name": "Grimy tarromin",
            "id": 203,
            "qty": 1
        }
    ]
},
{
    "name": "Tarromin potion (unf)",
    "skill": "Herblore",
    "level": 11,
    "xp": 0.0,
    "output_id": 95,
    "output_qty": 1,
    "members": True,
    "hourly_actions": 2500,
    "materials": [
        {
            "name": "Tarromin",
            "id": 253,
            "qty": 1
        },
        {
            "name": "Vial of water",
            "id": 227,
            "qty": 1
        }
    ]
},
{
    "name": "Clean Harralander",
    "skill": "Herblore",
    "level": 20,
    "xp": 6.3,
    "output_id": 255,
    "output_qty": 1,
    "members": True,
    "hourly_actions": 3500,
    "materials": [
        {
            "name": "Grimy harralander",
            "id": 205,
            "qty": 1
        }
    ]
},
{
    "name": "Harralander potion (unf)",
    "skill": "Herblore",
    "level": 20,
    "xp": 0.0,
    "output_id": 97,
    "output_qty": 1,
    "members": True,
    "hourly_actions": 2500,
    "materials": [
        {
            "name": "Harralander",
            "id": 255,
            "qty": 1
        },
        {
            "name": "Vial of water",
            "id": 227,
            "qty": 1
        }
    ]
},
{
    "name": "Clean Irit leaf",
    "skill": "Herblore",
    "level": 40,
    "xp": 8.8,
    "output_id": 259,
    "output_qty": 1,
    "members": True,
    "hourly_actions": 3500,
    "materials": [
        {
            "name": "Grimy irit leaf",
            "id": 209,
            "qty": 1
        }
    ]
},
{
    "name": "Irit potion (unf)",
    "skill": "Herblore",
    "level": 40,
    "xp": 0.0,
    "output_id": 101,
    "output_qty": 1,
    "members": True,
    "hourly_actions": 2500,
    "materials": [
        {
            "name": "Irit leaf",
            "id": 259,
            "qty": 1
        },
        {
            "name": "Vial of water",
            "id": 227,
            "qty": 1
        }
    ]
},
{
    "name": "Clean Avantoe",
    "skill": "Herblore",
    "level": 48,
    "xp": 10.0,
    "output_id": 261,
    "output_qty": 1,
    "members": True,
    "hourly_actions": 3500,
    "materials": [
        {
            "name": "Grimy avantoe",
            "id": 211,
            "qty": 1
        }
    ]
},
{
    "name": "Clean Kwuarm",
    "skill": "Herblore",
    "level": 54,
    "xp": 11.3,
    "output_id": 263,
    "output_qty": 1,
    "members": True,
    "hourly_actions": 3500,
    "materials": [
        {
            "name": "Grimy kwuarm",
            "id": 213,
            "qty": 1
        }
    ]
},
{
    "name": "Clean Cadantine",
    "skill": "Herblore",
    "level": 65,
    "xp": 12.5,
    "output_id": 265,
    "output_qty": 1,
    "members": True,
    "hourly_actions": 3500,
    "materials": [
        {
            "name": "Grimy cadantine",
            "id": 215,
            "qty": 1
        }
    ]
},
{
    "name": "Clean Lantadyme",
    "skill": "Herblore",
    "level": 67,
    "xp": 13.1,
    "output_id": 2481,
    "output_qty": 1,
    "members": True,
    "hourly_actions": 3500,
    "materials": [
        {
            "name": "Grimy lantadyme",
            "id": 2485,
            "qty": 1
        }
    ]
},
{
    "name": "Lantadyme potion (unf)",
    "skill": "Herblore",
    "level": 67,
    "xp": 0.0,
    "output_id": 2483,
    "output_qty": 1,
    "members": True,
    "hourly_actions": 2500,
    "materials": [
        {
            "name": "Lantadyme",
            "id": 2481,
            "qty": 1
        },
        {
            "name": "Vial of water",
            "id": 227,
            "qty": 1
        }
    ]
},
{
    "name": "Clean Dwarf weed",
    "skill": "Herblore",
    "level": 70,
    "xp": 13.8,
    "output_id": 267,
    "output_qty": 1,
    "members": True,
    "hourly_actions": 3500,
    "materials": [
        {
            "name": "Grimy dwarf weed",
            "id": 217,
            "qty": 1
        }
    ]
},
{
    "name": "Dwarf weed potion (unf)",
    "skill": "Herblore",
    "level": 70,
    "xp": 0.0,
    "output_id": 109,
    "output_qty": 1,
    "members": True,
    "hourly_actions": 2500,
    "materials": [
        {
            "name": "Dwarf weed",
            "id": 267,
            "qty": 1
        },
        {
            "name": "Vial of water",
            "id": 227,
            "qty": 1
        }
    ]
},
{
    "name": "Clean Torstol",
    "skill": "Herblore",
    "level": 75,
    "xp": 15.0,
    "output_id": 269,
    "output_qty": 1,
    "members": True,
    "hourly_actions": 3500,
    "materials": [
        {
            "name": "Grimy torstol",
            "id": 219,
            "qty": 1
        }
    ]
},
{
    "name": "Cut Opal",
    "skill": "Crafting",
    "level": 1,
    "xp": 15.0,
    "output_id": 1609,
    "output_qty": 1,
    "members": True,
    "hourly_actions": 2400,
    "materials": [
        {
            "name": "Uncut opal",
            "id": 1625,
            "qty": 1
        }
    ]
},
{
    "name": "Cut Jade",
    "skill": "Crafting",
    "level": 13,
    "xp": 20.0,
    "output_id": 1611,
    "output_qty": 1,
    "members": True,
    "hourly_actions": 2400,
    "materials": [
        {
            "name": "Uncut jade",
            "id": 1627,
            "qty": 1
        }
    ]
},
{
    "name": "Cut Red topaz",
    "skill": "Crafting",
    "level": 16,
    "xp": 25.0,
    "output_id": 1613,
    "output_qty": 1,
    "members": True,
    "hourly_actions": 2400,
    "materials": [
        {
            "name": "Uncut red topaz",
            "id": 1629,
            "qty": 1
        }
    ]
},
{
    "name": "Empty candle lantern",
    "skill": "Crafting",
    "level": 4,
    "xp": 19.0,
    "output_id": 4527,
    "output_qty": 1,
    "members": True,
    "hourly_actions": 1800,
    "materials": [
        {
            "name": "Molten glass",
            "id": 1775,
            "qty": 1
        }
    ]
},
{
    "name": "Empty oil lamp",
    "skill": "Crafting",
    "level": 12,
    "xp": 25.0,
    "output_id": 4525,
    "output_qty": 1,
    "members": True,
    "hourly_actions": 1800,
    "materials": [
        {
            "name": "Molten glass",
            "id": 1775,
            "qty": 1
        }
    ]
},
{
    "name": "Empty fishbowl",
    "skill": "Crafting",
    "level": 42,
    "xp": 42.5,
    "output_id": 6667,
    "output_qty": 1,
    "members": True,
    "hourly_actions": 1800,
    "materials": [
        {
            "name": "Molten glass",
            "id": 1775,
            "qty": 1
        }
    ]
},
{
    "name": "Opal bolts (e) (x10)",
    "skill": "Magic",
    "level": 4,
    "xp": 9.0,
    "output_id": 9236,
    "output_qty": 10,
    "members": True,
    "hourly_actions": 2500,
    "materials": [
        {
            "name": "Opal bolts",
            "id": 879,
            "qty": 10
        },
        {
            "name": "Cosmic rune",
            "id": 564,
            "qty": 1
        },
        {
            "name": "Air rune",
            "id": 556,
            "qty": 2
        }
    ]
},
{
    "name": "Pearl bolts (e) (x10)",
    "skill": "Magic",
    "level": 24,
    "xp": 29.0,
    "output_id": 9238,
    "output_qty": 10,
    "members": True,
    "hourly_actions": 2500,
    "materials": [
        {
            "name": "Pearl bolts",
            "id": 880,
            "qty": 10
        },
        {
            "name": "Cosmic rune",
            "id": 564,
            "qty": 1
        },
        {
            "name": "Water rune",
            "id": 555,
            "qty": 2
        }
    ]
},
{
    "name": "Topaz bolts (e) (x10)",
    "skill": "Magic",
    "level": 29,
    "xp": 33.0,
    "output_id": 9239,
    "output_qty": 10,
    "members": True,
    "hourly_actions": 2500,
    "materials": [
        {
            "name": "Topaz bolts",
            "id": 9336,
            "qty": 10
        },
        {
            "name": "Cosmic rune",
            "id": 564,
            "qty": 1
        },
        {
            "name": "Fire rune",
            "id": 554,
            "qty": 2
        }
    ]
},
{
    "name": "Sapphire bolts (e) (x10)",
    "skill": "Magic",
    "level": 7,
    "xp": 17.5,
    "output_id": 9240,
    "output_qty": 10,
    "members": True,
    "hourly_actions": 2500,
    "materials": [
        {
            "name": "Sapphire bolts",
            "id": 9337,
            "qty": 10
        },
        {
            "name": "Cosmic rune",
            "id": 564,
            "qty": 1
        },
        {
            "name": "Water rune",
            "id": 555,
            "qty": 1
        },
        {
            "name": "Mind rune",
            "id": 558,
            "qty": 1
        }
    ]
},
{
    "name": "Emerald bolts (e) (x10)",
    "skill": "Magic",
    "level": 27,
    "xp": 37.0,
    "output_id": 9241,
    "output_qty": 10,
    "members": True,
    "hourly_actions": 2500,
    "materials": [
        {
            "name": "Emerald bolts",
            "id": 9338,
            "qty": 10
        },
        {
            "name": "Cosmic rune",
            "id": 564,
            "qty": 1
        },
        {
            "name": "Air rune",
            "id": 556,
            "qty": 2
        },
        {
            "name": "Nature rune",
            "id": 561,
            "qty": 1
        }
    ]
},
{
    "name": "Ruby bolts (e) (x10)",
    "skill": "Magic",
    "level": 49,
    "xp": 59.0,
    "output_id": 9242,
    "output_qty": 10,
    "members": True,
    "hourly_actions": 2500,
    "materials": [
        {
            "name": "Ruby bolts",
            "id": 9339,
            "qty": 10
        },
        {
            "name": "Cosmic rune",
            "id": 564,
            "qty": 1
        },
        {
            "name": "Fire rune",
            "id": 554,
            "qty": 5
        },
        {
            "name": "Blood rune",
            "id": 565,
            "qty": 1
        }
    ]
},
{
    "name": "Diamond bolts (e) (x10)",
    "skill": "Magic",
    "level": 57,
    "xp": 67.0,
    "output_id": 9243,
    "output_qty": 10,
    "members": True,
    "hourly_actions": 2500,
    "materials": [
        {
            "name": "Diamond bolts",
            "id": 9340,
            "qty": 10
        },
        {
            "name": "Cosmic rune",
            "id": 564,
            "qty": 1
        },
        {
            "name": "Earth rune",
            "id": 557,
            "qty": 2
        },
        {
            "name": "Law rune",
            "id": 563,
            "qty": 1
        }
    ]
},
{
    "name": "Dragonstone bolts (e) (x10)",
    "skill": "Magic",
    "level": 68,
    "xp": 78.0,
    "output_id": 9244,
    "output_qty": 10,
    "members": True,
    "hourly_actions": 2500,
    "materials": [
        {
            "name": "Dragonstone bolts",
            "id": 9341,
            "qty": 10
        },
        {
            "name": "Cosmic rune",
            "id": 564,
            "qty": 1
        },
        {
            "name": "Earth rune",
            "id": 557,
            "qty": 15
        },
        {
            "name": "Soul rune",
            "id": 566,
            "qty": 1
        }
    ]
},
{
    "name": "Onyx bolts (e) (x10)",
    "skill": "Magic",
    "level": 87,
    "xp": 97.0,
    "output_id": 9245,
    "output_qty": 10,
    "members": True,
    "hourly_actions": 2500,
    "materials": [
        {
            "name": "Onyx bolts",
            "id": 9342,
            "qty": 10
        },
        {
            "name": "Cosmic rune",
            "id": 564,
            "qty": 1
        },
        {
            "name": "Fire rune",
            "id": 554,
            "qty": 20
        },
        {
            "name": "Death rune",
            "id": 560,
            "qty": 1
        }
    ]
},
{
    "name": "Spin Flax (x5)",
    "skill": "Magic",
    "level": 76,
    "xp": 75.0,
    "output_id": 1777,
    "output_qty": 5,
    "members": True,
    "hourly_actions": 1200,
    "materials": [
        {
            "name": "Flax",
            "id": 1779,
            "qty": 5
        },
        {
            "name": "Astral rune",
            "id": 9075,
            "qty": 2
        },
        {
            "name": "Nature rune",
            "id": 561,
            "qty": 5
        },
        {
            "name": "Air rune",
            "id": 556,
            "qty": 1
        }
    ]
},
{
    "name": "Tan Black Leather (x5)",
    "skill": "Magic",
    "level": 78,
    "xp": 81.0,
    "output_id": 2509,
    "output_qty": 5,
    "members": True,
    "hourly_actions": 1200,
    "materials": [
        {
            "name": "Black dragonhide",
            "id": 1747,
            "qty": 5
        },
        {
            "name": "Astral rune",
            "id": 9075,
            "qty": 2
        },
        {
            "name": "Nature rune",
            "id": 561,
            "qty": 1
        },
        {
            "name": "Fire rune",
            "id": 554,
            "qty": 5
        }
    ]
},
{
    "name": "Tan Blue Leather (x5)",
    "skill": "Magic",
    "level": 78,
    "xp": 81.0,
    "output_id": 2505,
    "output_qty": 5,
    "members": True,
    "hourly_actions": 1200,
    "materials": [
        {
            "name": "Blue dragonhide",
            "id": 1751,
            "qty": 5
        },
        {
            "name": "Astral rune",
            "id": 9075,
            "qty": 2
        },
        {
            "name": "Nature rune",
            "id": 561,
            "qty": 1
        },
        {
            "name": "Fire rune",
            "id": 554,
            "qty": 5
        }
    ]
},
{
    "name": "Tan Red Leather (x5)",
    "skill": "Magic",
    "level": 78,
    "xp": 81.0,
    "output_id": 2507,
    "output_qty": 5,
    "members": True,
    "hourly_actions": 1200,
    "materials": [
        {
            "name": "Red dragonhide",
            "id": 1749,
            "qty": 5
        },
        {
            "name": "Astral rune",
            "id": 9075,
            "qty": 2
        },
        {
            "name": "Nature rune",
            "id": 561,
            "qty": 1
        },
        {
            "name": "Fire rune",
            "id": 554,
            "qty": 5
        }
    ]
},
{
    "name": "Tan Green Leather (x5)",
    "skill": "Magic",
    "level": 78,
    "xp": 81.0,
    "output_id": 1745,
    "output_qty": 5,
    "members": True,
    "hourly_actions": 1200,
    "materials": [
        {
            "name": "Green dragonhide",
            "id": 1753,
            "qty": 5
        },
        {
            "name": "Astral rune",
            "id": 9075,
            "qty": 2
        },
        {
            "name": "Nature rune",
            "id": 561,
            "qty": 1
        },
        {
            "name": "Fire rune",
            "id": 554,
            "qty": 5
        }
    ]
},
{
    "name": "Superheat Runite Bar",
    "skill": "Magic",
    "level": 43,
    "xp": 53.0,
    "output_id": 2363,
    "output_qty": 1,
    "members": False,
    "hourly_actions": 1800,
    "materials": [
        {
            "name": "Runite ore",
            "id": 451,
            "qty": 1
        },
        {
            "name": "Coal",
            "id": 453,
            "qty": 8
        },
        {
            "name": "Nature rune",
            "id": 561,
            "qty": 1
        },
        {
            "name": "Fire rune",
            "id": 554,
            "qty": 4
        }
    ]
},
{
    "name": "Superheat Adamant Bar",
    "skill": "Magic",
    "level": 43,
    "xp": 37.5,
    "output_id": 2361,
    "output_qty": 1,
    "members": False,
    "hourly_actions": 1800,
    "materials": [
        {
            "name": "Adamantite ore",
            "id": 449,
            "qty": 1
        },
        {
            "name": "Coal",
            "id": 453,
            "qty": 6
        },
        {
            "name": "Nature rune",
            "id": 561,
            "qty": 1
        },
        {
            "name": "Fire rune",
            "id": 554,
            "qty": 4
        }
    ]
},
{
    "name": "Superheat Mithril Bar",
    "skill": "Magic",
    "level": 43,
    "xp": 30.0,
    "output_id": 2359,
    "output_qty": 1,
    "members": False,
    "hourly_actions": 1800,
    "materials": [
        {
            "name": "Mithril ore",
            "id": 447,
            "qty": 1
        },
        {
            "name": "Coal",
            "id": 453,
            "qty": 4
        },
        {
            "name": "Nature rune",
            "id": 561,
            "qty": 1
        },
        {
            "name": "Fire rune",
            "id": 554,
            "qty": 4
        }
    ]
},
{
    "name": "Superheat Steel Bar",
    "skill": "Magic",
    "level": 43,
    "xp": 17.5,
    "output_id": 2353,
    "output_qty": 1,
    "members": False,
    "hourly_actions": 1800,
    "materials": [
        {
            "name": "Iron ore",
            "id": 440,
            "qty": 1
        },
        {
            "name": "Coal",
            "id": 453,
            "qty": 2
        },
        {
            "name": "Nature rune",
            "id": 561,
            "qty": 1
        },
        {
            "name": "Fire rune",
            "id": 554,
            "qty": 4
        }
    ]
},
{
    "name": "Cooked trout",
    "skill": "Cooking",
    "level": 15,
    "xp": 70.0,
    "output_id": 333,
    "output_qty": 1,
    "members": False,
    "hourly_actions": 1400,
    "materials": [
        {
            "name": "Raw trout",
            "id": 335,
            "qty": 1
        }
    ]
},
{
    "name": "Cooked salmon",
    "skill": "Cooking",
    "level": 25,
    "xp": 90.0,
    "output_id": 329,
    "output_qty": 1,
    "members": False,
    "hourly_actions": 1400,
    "materials": [
        {
            "name": "Raw salmon",
            "id": 331,
            "qty": 1
        }
    ]
},
{
    "name": "Cooked tuna",
    "skill": "Cooking",
    "level": 30,
    "xp": 100.0,
    "output_id": 361,
    "output_qty": 1,
    "members": False,
    "hourly_actions": 1400,
    "materials": [
        {
            "name": "Raw tuna",
            "id": 359,
            "qty": 1
        }
    ]
},
{
    "name": "Cooked bass",
    "skill": "Cooking",
    "level": 43,
    "xp": 130.0,
    "output_id": 365,
    "output_qty": 1,
    "members": False,
    "hourly_actions": 1400,
    "materials": [
        {
            "name": "Raw bass",
            "id": 363,
            "qty": 1
        }
    ]
},
{
    "name": "Plain pizza",
    "skill": "Cooking",
    "level": 35,
    "xp": 143.0,
    "output_id": 2289,
    "output_qty": 1,
    "members": False,
    "hourly_actions": 1600,
    "materials": [
        {
            "name": "Pizza base",
            "id": 2283,
            "qty": 1
        },
        {
            "name": "Tomato",
            "id": 1982,
            "qty": 1
        },
        {
            "name": "Cheese",
            "id": 1985,
            "qty": 1
        }
    ]
},
{
    "name": "Meat pizza",
    "skill": "Cooking",
    "level": 45,
    "xp": 26.0,
    "output_id": 2293,
    "output_qty": 1,
    "members": False,
    "hourly_actions": 2000,
    "materials": [
        {
            "name": "Plain pizza",
            "id": 2289,
            "qty": 1
        },
        {
            "name": "Cooked meat",
            "id": 2142,
            "qty": 1
        }
    ]
},
{
    "name": "Pineapple pizza",
    "skill": "Cooking",
    "level": 65,
    "xp": 45.0,
    "output_id": 2301,
    "output_qty": 1,
    "members": True,
    "hourly_actions": 2000,
    "materials": [
        {
            "name": "Plain pizza",
            "id": 2289,
            "qty": 1
        },
        {
            "name": "Pineapple ring",
            "id": 2118,
            "qty": 1
        }
    ]
},
{
    "name": "Ball of wool",
    "skill": "Crafting",
    "level": 1,
    "xp": 2.5,
    "output_id": 1759,
    "output_qty": 1,
    "members": False,
    "hourly_actions": 1800,
    "materials": [
        {
            "name": "Wool",
            "id": 1737,
            "qty": 1
        }
    ]
},
{
    "name": "Magic string",
    "skill": "Crafting",
    "level": 19,
    "xp": 30.0,
    "output_id": 6038,
    "output_qty": 1,
    "members": True,
    "hourly_actions": 1800,
    "materials": [
        {
            "name": "Magic roots",
            "id": 6051,
            "qty": 1
        }
    ]
},
{
    "name": "Rope",
    "skill": "Crafting",
    "level": 30,
    "xp": 25.0,
    "output_id": 954,
    "output_qty": 1,
    "members": True,
    "hourly_actions": 1800,
    "materials": [
        {
            "name": "Ball of wool",
            "id": 1759,
            "qty": 4
        }
    ]
},
{
    "name": "Pot",
    "skill": "Crafting",
    "level": 1,
    "xp": 12.5,
    "output_id": 1931,
    "output_qty": 1,
    "members": False,
    "hourly_actions": 1200,
    "materials": [
        {
            "name": "Soft clay",
            "id": 1761,
            "qty": 1
        }
    ]
},
{
    "name": "Bowl",
    "skill": "Crafting",
    "level": 8,
    "xp": 15.0,
    "output_id": 1923,
    "output_qty": 1,
    "members": False,
    "hourly_actions": 1200,
    "materials": [
        {
            "name": "Soft clay",
            "id": 1761,
            "qty": 1
        }
    ]
},
{
    "name": "Plant pot",
    "skill": "Crafting",
    "level": 19,
    "xp": 37.5,
    "output_id": 5350,
    "output_qty": 1,
    "members": True,
    "hourly_actions": 1200,
    "materials": [
        {
            "name": "Soft clay",
            "id": 1761,
            "qty": 1
        }
    ]
}
]
