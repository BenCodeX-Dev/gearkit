# Gearkit

A Python script that generates a Minecraft datapack. One command in the game then hands you 29 shulker boxes of fully enchanted gear, potions, books and supplies.

The generated datapack is checked in, so you can use it without running Python.

## What is in the boxes

| Boxes | Count | Contents |
|---|---|---|
| Gear | 10 | Full netherite armour, sword, axe, two bows, two crossbows, two tridents, two maces, two pickaxes, shovel, shears, fishing rod, shield, elytra, a totem, 64 rockets, three stacks of arrows and 16 enchanted golden apples. All 27 slots are used. |
| Potions | 10 | 42 potion types in three forms (drinkable, splash, lingering), two of each. That is 252 stacks. |
| Books | 2 | All 40 enchantments at their highest level, plus 14 spare books of the ones you apply most. |
| Totems | 1 | 27 totems. They do not stack, so each takes a slot. |
| Rockets | 1 | 27 stacks of 64, which is 1728 rockets with flight duration 3. |
| Mobility | 1 | Ender pearls, chorus fruit, wind charges, an elytra with rockets, buckets, obsidian, ender chests, respawn anchors, beds, scaffolding, boats, minecarts and rails. |
| Food and blocks | 1 | Golden apples, golden carrots, meat, cake, and building blocks from cobblestone to netherite. |
| Station | 1 | Five beacons with 192 netherite blocks, conduits, anvils, an enchanting and a smithing table, a brewing set-up and experience bottles. |
| Tipped arrows | 2 | All 42 potion types as arrows, 64 each. |

The ten gear boxes come in six variants. They differ in the protection type on the armour and the damage type on the weapons.

## Rules the generator follows

Every enchantment is at its vanilla maximum, never above it. Protection is IV, Sharpness is V, and so on.

There are no fire enchantments. `fire_aspect` and `flame` are left out. `fire_protection` is in, because it protects against fire.

Enchantments that cannot share an item are split over two items instead of being dropped:

- a bow with Infinity and a bow with Mending
- a crossbow with Piercing and one with Multishot
- a trident with Loyalty and one with Riptide
- a mace with Density and one with Breach
- a pickaxe with Fortune and one with Silk Touch

## Where the boxes go

Six boxes go into your ender chest, slots 0 to 5: gear, potions, books, totems, rockets and mobility.

The other 23 are placed on the ground, 15 blocks in front of you, five to a row and two blocks apart. Each box drops to the first solid block below it, so it lands on the surface and not in the air.

## Use it

You need permission to run functions: cheats switched on in your own world, or operator rights on a server.

1. Copy `out/gearkit_datapack/` into the `datapacks` folder of your world.
2. Run `/reload`.
3. Run `/function gearkit:all`.

The parts can also be run on their own:

```
/function gearkit:ender
/function gearkit:place
/function gearkit:give_all
```

`give_all` puts all 29 boxes into your inventory instead of placing them. An inventory has 36 slots, so it has to be almost empty, or the rest falls on the ground.

If you would rather not install a datapack, `out/commands.txt` holds every command as one line to paste into the chat or the server console. The longest one is 4723 characters. The commands that place boxes are relative to where you stand and where you look.

## Game versions

`out/` uses the item component syntax of Minecraft 1.21.5 and later.

`out_legacy/` is for 1.20.5 to 1.21.4. The contents are the same. Only the way enchantments are written differs.

If the game answers with `Expected value` or `Unknown component`, try the other folder.

## Build it again

```
python3 gen.py
LEGACY=1 python3 gen.py
```

The first line writes `out/`, the second writes `out_legacy/`. The script uses only the Python standard library. Running it reproduces the checked-in files exactly.

## What I have not verified

- `sweeping_edge` may have a different name in newer game versions. If a line fails because of it, only the sword is affected.
- `pack_format` is set to 61. If the game complains about the pack version, put in the number it names in the message.

The two messages the datapack prints in the chat are in German.

## License

MIT. See [LICENSE](LICENSE).
