"""Writes boxes.js for the page in this folder.

It reads the definitions in ../gen.py and stops before the part that writes
the datapack, so out/ and out_legacy/ are left alone.

    python3 site/export.py
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, "..", "gen.py")

src = open(GEN).read().split("# ---------------------------------------------------------------- write out")[0]
keep = "self.c = comps(ench, stored, potion, extra)"
assert keep in src
src = src.replace(keep, keep + "; self.raw = (ench, stored, potion, extra)")
ns = {"__file__": GEN}
exec(src, ns)

UTIL_NAMES = {
    "totem_of_undying": "Totems", "firework_rocket": "Rockets",
    "ender_pearl": "Mobility", "enchanted_golden_apple": "Food and blocks",
    "beacon": "Station", "tipped_arrow": "Tipped arrows",
}
variants = iter(ns["GEAR_VARIANTS"])
seen = {}
boxes = []
for kind, b in ns["ALL"]:
    items = []
    for it in b.items:
        ench, stored, potion, extra = it.raw
        d = {"id": it.id.split(":")[1], "n": it.count}
        if ench: d["e"] = ench
        if stored: d["s"] = stored
        if potion: d["p"] = potion
        if extra and "flight_duration:3" in extra: d["x"] = "flight duration 3"
        if items and {k: v for k, v in items[-1].items() if k != "k"} == d:
            items[-1]["k"] = items[-1].get("k", 1) + 1
        else:
            items.append(d)
    if kind == "gear":
        prot, dmg, _ = next(variants)
        name, note = "Gear", "%s, %s" % (prot.replace("_", " "), dmg.replace("_", " "))
    elif kind == "pot":
        name, note = "Potions", ""
    elif kind == "book":
        name, note = "Books", ""
    else:
        name, note = UTIL_NAMES[b.items[0].id.split(":")[1]], ""
    seen[name] = seen.get(name, 0) + 1
    boxes.append({"name": name, "note": note, "nr": seen[name],
                  "dye": b.block.split(":")[1].replace("_shulker_box", ""),
                  "ender": b in ns["ENDER"], "slots": len(b.items), "items": items})
for b in boxes:
    b["of"] = seen[b["name"]]

with open(os.path.join(HERE, "boxes.js"), "w") as f:
    f.write("window.BOXES=" + json.dumps(boxes, separators=(",", ":")) + ";\n")
print(len(boxes), "boxes,", sum(b["ender"] for b in boxes), "of them for the ender chest")
