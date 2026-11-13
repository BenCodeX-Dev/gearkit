#!/usr/bin/env python3
"""Generator: Minecraft Java (1.21.5+ component syntax) full max-gear kit.

Emits:
  out/gearkit_datapack/      -> drop into world/datapacks/, run /function gearkit:all
  out/commands.txt           -> every command as plain text for manual paste

Rules baked in:
  - no fire enchantments (fire_aspect, flame)
  - vanilla max levels only, never 255
"""
import os, json, shutil

LEGACY = os.environ.get("LEGACY") == "1"   # pre-1.21.5 enchantment component shape
NS = "gearkit"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "out_legacy" if LEGACY else "out")
DP = os.path.join(OUT, "gearkit_datapack")
FN = os.path.join(DP, "data", NS, "function")

# ---------------------------------------------------------------- helpers
def snbt_ench(d, key="minecraft:enchantments"):
    inner = ",".join('"minecraft:%s":%d' % (k, v) for k, v in d.items())
    if LEGACY:                      # 1.20.5 - 1.21.4 wrapped the map in levels:{}
        return '"%s":{levels:{%s}}' % (key, inner)
    return '"%s":{%s}' % (key, inner)

def comps(ench=None, stored=None, potion=None, extra=None):
    parts = []
    if ench:
        parts.append(snbt_ench(ench))
    if stored:
        parts.append(snbt_ench(stored, "minecraft:stored_enchantments"))
    if potion:
        parts.append('"minecraft:potion_contents":{potion:"minecraft:%s"}' % potion)
    if extra:
        parts.append(extra)
    return ",".join(parts)

class It:
    """One item stack."""
    def __init__(self, id_, count=1, ench=None, stored=None, potion=None, extra=None):
        self.id, self.count = "minecraft:" + id_, count
        self.c = comps(ench, stored, potion, extra)

    def as_container_entry(self, slot):
        c = (",components:{%s}" % self.c) if self.c else ""
        return "{slot:%d,item:{id:\"%s\",count:%d%s}}" % (slot, self.id, self.count, c)

    def as_block_entry(self, slot):
        c = (",components:{%s}" % self.c) if self.c else ""
        return "{Slot:%db,id:\"%s\",count:%d%s}" % (slot, self.id, self.count, c)

    def as_give_arg(self):
        b = ("[%s]" % self.c.replace('"minecraft:enchantments"', "minecraft:enchantments")
             .replace('"minecraft:stored_enchantments"', "minecraft:stored_enchantments")
             .replace('"minecraft:potion_contents"', "minecraft:potion_contents")) if self.c else ""
        return self.id + b

class Box:
    """One shulker box with up to 27 stacks."""
    def __init__(self, block, items):
        assert len(items) <= 27, len(items)
        self.block, self.items = "minecraft:" + block, items

    def item_form(self):
        inner = ",".join(i.as_container_entry(n) for n, i in enumerate(self.items))
        return "%s[minecraft:container=[%s]]" % (self.block, inner)

    def block_form(self):
        inner = ",".join(i.as_block_entry(n) for n, i in enumerate(self.items))
        return "%s{Items:[%s]}" % (self.block, inner)

# ---------------------------------------------------------------- enchant data
# vanilla max levels; fire_aspect + flame deliberately excluded
MAXLVL = {
    "protection": 4, "fire_protection": 4, "feather_falling": 4, "blast_protection": 4,
    "projectile_protection": 4, "respiration": 3, "aqua_affinity": 1, "thorns": 3,
    "depth_strider": 3, "frost_walker": 2, "binding_curse": 1, "soul_speed": 3,
    "swift_sneak": 3, "sharpness": 5, "smite": 5, "bane_of_arthropods": 5,
    "knockback": 2, "looting": 3, "sweeping_edge": 3, "efficiency": 5,
    "silk_touch": 1, "unbreaking": 3, "fortune": 3, "power": 5, "punch": 2,
    "infinity": 1, "luck_of_the_sea": 3, "lure": 3, "loyalty": 3, "impaling": 5,
    "riptide": 3, "channeling": 1, "multishot": 1, "quick_charge": 3, "piercing": 4,
    "density": 5, "breach": 4, "wind_burst": 3, "mending": 1, "vanishing_curse": 1,
}
UM = {"unbreaking": 3, "mending": 1}
ROCKET3 = '"minecraft:fireworks":{flight_duration:3,explosions:[]}'   # elytra rockets

def E(*names, **extra):
    d = {n: MAXLVL[n] for n in names}
    d.update(extra)
    return d

# ---------------------------------------------------------------- gear boxes
# (armour protection variant, melee damage variant, shulker colour)
GEAR_VARIANTS = [
    ("protection",            "sharpness",          "blue"),
    ("protection",            "sharpness",          "light_blue"),
    ("protection",            "sharpness",          "cyan"),
    ("protection",            "sharpness",          "blue"),
    ("blast_protection",      "smite",              "gray"),
    ("blast_protection",      "smite",              "light_gray"),
    ("projectile_protection", "bane_of_arthropods", "green"),
    ("fire_protection",       "sharpness",          "orange"),
    ("protection",            "smite",              "white"),
    ("blast_protection",      "bane_of_arthropods", "lime"),
]

def gear_box(prot, dmg, colour):
    items = [
        It("netherite_helmet",     ench=E(prot, "respiration", "aqua_affinity", "thorns", **UM)),
        It("netherite_chestplate", ench=E(prot, "thorns", **UM)),
        It("netherite_leggings",   ench=E(prot, "thorns", "swift_sneak", **UM)),
        # depth_strider chosen over frost_walker (mutually exclusive)
        It("netherite_boots",      ench=E(prot, "thorns", "feather_falling", "depth_strider", "soul_speed", **UM)),
        It("netherite_sword",      ench=E(dmg, "looting", "knockback", "sweeping_edge", **UM)),
        It("netherite_axe",        ench=E(dmg, "efficiency", "fortune", **UM)),
        # infinity and mending are mutually exclusive -> one bow of each
        It("bow",                  ench=E("power", "punch", "infinity", unbreaking=3)),
        It("bow",                  ench=E("power", "punch", **UM)),
        # piercing and multishot are mutually exclusive
        It("crossbow",             ench=E("quick_charge", "piercing", **UM)),
        It("crossbow",             ench=E("quick_charge", "multishot", **UM)),
        # loyalty and riptide are mutually exclusive
        It("trident",              ench=E("impaling", "loyalty", "channeling", **UM)),
        It("trident",              ench=E("impaling", "riptide", **UM)),
        # density and breach are mutually exclusive
        It("mace",                 ench=E("density", "wind_burst", **UM)),
        It("mace",                 ench=E("breach", "wind_burst", **UM)),
        # fortune and silk_touch are mutually exclusive
        It("netherite_pickaxe",    ench=E("efficiency", "fortune", **UM)),
        It("netherite_pickaxe",    ench=E("efficiency", "silk_touch", **UM)),
        It("netherite_shovel",     ench=E("efficiency", "fortune", **UM)),
        It("shears",               ench=E("efficiency", "silk_touch", **UM)),
        It("totem_of_undying"),
        It("fishing_rod",          ench=E("luck_of_the_sea", "lure", **UM)),
        It("shield",               ench=E(**UM)),
        It("elytra",               ench=E(**UM)),
        It("firework_rocket", 64, extra=ROCKET3),
        It("arrow", 64),
        It("tipped_arrow", 64, potion="strong_harming"),
        It("tipped_arrow", 64, potion="strong_poison"),
        It("enchanted_golden_apple", 16),
    ]
    return Box(colour + "_shulker_box", items)

GEAR = [gear_box(*v) for v in GEAR_VARIANTS]

# ---------------------------------------------------------------- book boxes
BOOK_ORDER = [k for k in MAXLVL]  # 40 entries, fire ones already absent
books = [It("enchanted_book", stored={k: MAXLVL[k]}) for k in BOOK_ORDER]
# pad box 2 with spares of the enchantments you re-apply most
spares = ["mending", "unbreaking", "protection", "sharpness", "power", "efficiency",
          "fortune", "looting", "feather_falling", "thorns", "impaling", "density",
          "quick_charge", "swift_sneak"]
books += [It("enchanted_book", stored={k: MAXLVL[k]}) for k in spares]
BOOKS = [Box("purple_shulker_box", books[i:i + 27]) for i in range(0, len(books), 27)]

# ---------------------------------------------------------------- potion boxes
POTIONS = [
    "night_vision", "long_night_vision",
    "invisibility", "long_invisibility",
    "leaping", "long_leaping", "strong_leaping",
    "fire_resistance", "long_fire_resistance",
    "swiftness", "long_swiftness", "strong_swiftness",
    "slowness", "long_slowness", "strong_slowness",
    "turtle_master", "long_turtle_master", "strong_turtle_master",
    "water_breathing", "long_water_breathing",
    "healing", "strong_healing",
    "harming", "strong_harming",
    "poison", "long_poison", "strong_poison",
    "regeneration", "long_regeneration", "strong_regeneration",
    "strength", "long_strength", "strong_strength",
    "weakness", "long_weakness",
    "luck",
    "slow_falling", "long_slow_falling",
    "wind_charged", "weaving", "oozing", "infested",
]
pot_items = []
for form in ("potion", "splash_potion", "lingering_potion"):
    for p in POTIONS:
        pot_items.append(It(form, potion=p))
pot_items = pot_items * 2  # 2 copies of every potion/form -> 252 stacks
POT_COLOURS = ["magenta", "pink", "purple", "red", "magenta", "pink",
               "purple", "red", "magenta", "pink"]
per = -(-len(pot_items) // 10)
POTS = [Box(POT_COLOURS[i] + "_shulker_box", pot_items[i * per:(i + 1) * per])
        for i in range(10)]

# ---------------------------------------------------------------- utility boxes
# totems do not stack, so one slot each
TOTEMS = Box("yellow_shulker_box", [It("totem_of_undying") for _ in range(27)])

# 27 x 64 = 1728 flight-3 rockets
ROCKETS = Box("orange_shulker_box",
              [It("firework_rocket", 64, extra=ROCKET3) for _ in range(27)])

MOBILITY = Box("light_blue_shulker_box", [
    It("ender_pearl", 16), It("ender_pearl", 16), It("ender_pearl", 16),
    It("chorus_fruit", 64), It("wind_charge", 64), It("wind_charge", 64),
    It("elytra", ench=E(**UM)),
    It("firework_rocket", 64, extra=ROCKET3),
    It("water_bucket"), It("lava_bucket"), It("powder_snow_bucket"),
    It("obsidian", 64), It("crying_obsidian", 64), It("ender_chest", 8),
    It("respawn_anchor", 4), It("glowstone", 64),
    It("white_bed"), It("scaffolding", 64), It("ladder", 64),
    It("cobweb", 64), It("slime_block", 64), It("honey_block", 64),
    It("oak_boat"), It("minecart"), It("rail", 64),
    It("twisting_vines", 64), It("hay_block", 64),
])

FOOD_BLOCKS = Box("brown_shulker_box", [
    It("enchanted_golden_apple", 64), It("enchanted_golden_apple", 64),
    It("golden_apple", 64), It("golden_carrot", 64), It("cooked_beef", 64),
    It("cooked_porkchop", 64), It("bread", 64), It("milk_bucket"),
    It("cake"), It("honey_bottle", 16), It("dried_kelp_block", 64),
    It("obsidian", 64), It("netherite_block", 64), It("iron_block", 64),
    It("gold_block", 64), It("diamond_block", 64), It("emerald_block", 64),
    It("cobblestone", 64), It("dirt", 64), It("sand", 64), It("gravel", 64),
    It("oak_planks", 64), It("torch", 64), It("tnt", 64),
    It("flint_and_steel"), It("bucket", 16), It("string", 64),
])

STATION = Box("cyan_shulker_box", [
    It("beacon", 5), It("netherite_block", 64), It("netherite_block", 64),
    It("netherite_block", 64), It("conduit", 8), It("anvil", 16),
    It("grindstone", 4), It("smithing_table", 4), It("enchanting_table", 4),
    It("bookshelf", 64), It("brewing_stand", 8), It("cauldron", 8),
    It("blaze_powder", 64), It("nether_wart", 64), It("glowstone_dust", 64),
    It("redstone", 64), It("gunpowder", 64), It("dragon_breath", 64),
    It("glass_bottle", 64), It("experience_bottle", 64), It("experience_bottle", 64),
    It("lapis_lazuli", 64), It("shulker_shell", 64), It("ender_eye", 64),
    It("name_tag", 64), It("crafting_table", 16), It("furnace", 16),
])

# one tipped arrow stack per potion type (42 types -> 2 boxes)
tipped = [It("tipped_arrow", 64, potion=p) for p in POTIONS]
TIPPED = [Box("gray_shulker_box", tipped[i:i + 27]) for i in range(0, len(tipped), 27)]

UTIL = [TOTEMS, ROCKETS, MOBILITY, FOOD_BLOCKS, STATION] + TIPPED

# ---------------------------------------------------------------- assemble
ALL = ([("gear", b) for b in GEAR] + [("pot", b) for b in POTS] +
       [("book", b) for b in BOOKS] + [("util", b) for b in UTIL])
# enderchest: one box per category you actually carry into a fight
ENDER = [GEAR[0], POTS[0], BOOKS[0], TOTEMS, ROCKETS, MOBILITY]
GROUND = [b for _, b in ALL if b not in ENDER]

# ---------------------------------------------------------------- write out
shutil.rmtree(OUT, ignore_errors=True)
os.makedirs(FN)

with open(os.path.join(DP, "pack.mcmeta"), "w") as f:
    json.dump({"pack": {
        "description": "Full max gear / potion / book kit",
        "pack_format": 61,
        "supported_formats": {"min_inclusive": 26, "max_inclusive": 200},
        "min_format": 26, "max_format": 200}}, f, indent=2)

lines_txt = []

def w(name, lines):
    with open(os.path.join(FN, name + ".mcfunction"), "w") as f:
        f.write("\n".join(lines) + "\n")

# --- ender chest (3 boxes)
ender_cmds = ["item replace entity @s enderchest.%d with %s" % (i, b.item_form())
              for i, b in enumerate(ENDER)]
ender_cmds.append('tellraw @s {"text":"Enderchest: Gear / Potions / Books / Totems / Raketen / Mobility geladen.","color":"green"}')
w("ender", ender_cmds)

# --- ground placement: 5x4 grid, 2 blocks apart, origin 15 blocks ahead
place_lines = ["# origin: 15 blocks in front of you, horizontal facing only"]
for idx, b in enumerate(GROUND):
    col, row = idx % 5, idx // 5
    dx, dz = col * 2, row * 2
    place_lines.append(
        "execute rotated ~ 0 positioned ^%d ^ ^%d positioned ~ ~6 ~ run function %s:g%02d"
        % (dx - 4, 15 + dz, NS, idx))
    # per-box scan-down function
    w("g%02d" % idx, [
        "# Place the box if the block below is solid, otherwise fall one block and try again.",
        "# The placing line comes first: after the fall returns, a box sits below every",
        "# level above it, and a check at that point would stack a box on each one.",
        "# Below the world both checks fail, so nothing is placed and the fall ends.",
        "execute unless block ~ ~-1 ~ #minecraft:replaceable "
        "run setblock ~ ~ ~ %s replace" % b.block_form(),
        "execute if block ~ ~-1 ~ #minecraft:replaceable "
        "positioned ~ ~-1 ~ run function %s:g%02d" % (NS, idx),
    ])
place_lines.append('tellraw @s {"text":"Shulker platziert, 15 Bloecke vor dir.","color":"green"}')
w("place", place_lines)

w("all", ["function %s:ender" % NS, "function %s:place" % NS])

# --- give-everything fallback (no placement, straight into inventory)
give_lines = []
for kind, b in ALL:
    give_lines.append("give @s " + b.item_form())
w("give_all", give_lines)

# ---------------------------------------------------------------- commands.txt
lines_txt.append("# === ENDERCHEST (6 Shulker: Gear / Potions / Books / Totems / Raketen / Mobility) ===")
lines_txt += ["/" + c for c in ender_cmds[:-1]]
lines_txt.append("")
lines_txt.append("# === ALLE SHULKER ALS ITEM INS INVENTAR ===")
lines_txt += ["/" + c for c in give_lines]
lines_txt.append("")
lines_txt.append("# === RESTLICHE SHULKER AUF DEN BODEN (relativ, ~ ~ ~ = deine Position) ===")
for idx, b in enumerate(GROUND):
    col, row = idx % 5, idx // 5
    lines_txt.append("/execute rotated ~ 0 positioned ^%d ^ ^%d run setblock ~ ~ ~ %s replace"
                     % (col * 2 - 4, 15 + row * 2, b.block_form()))

with open(os.path.join(OUT, "commands.txt"), "w") as f:
    f.write("\n".join(lines_txt) + "\n")

# ---------------------------------------------------------------- report
longest = max(len(l) for l in lines_txt)
print("gear boxes  :", len(GEAR))
print("potion boxes:", len(POTS), "| potion stacks:", len(pot_items),
      "| types:", len(POTIONS), "x3 forms")
print("book boxes  :", len(BOOKS), "| books:", len(books),
      "| distinct enchants:", len(BOOK_ORDER))
print("util boxes  :", len(UTIL), "| total boxes:", len(ALL))
print("enderchest  :", len(ENDER), "| ground:", len(GROUND))
print("longest command:", longest, "chars (chat limit 32500)")
