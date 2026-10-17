"""Build a synthetic 'test dataset' in the same format: copies the sample, renumbers wells/records (+200) and renames areas.
Usage: python scripts/make_synthetic_dataset.py <sample-data> <out-dir>"""
import os, sys, json, re, shutil, glob
src, dst = sys.argv[1], sys.argv[2]
AM = {"SW-23": ("NW-31", "Northwest Block 31"), "SW-24": ("NW-32", "Northwest Block 32"), "NE-07": ("SE-41", "Southeast Block 41"), "NE-08": ("SE-42", "Southeast Block 42")}
def ren(t):
    t = re.sub(r"(WELL|INS|MNT|REG|CTX)-(\d{4})", lambda m: f"{m.group(1)}-{int(m.group(2)) + 200:04d}", t)
    for a, (b, n) in AM.items(): t = t.replace(f'"{a}"', f'"{b}"')
    return t
shutil.copytree(f"{src}/fleet", f"{dst}/fleet")
ar = json.load(open(f"{src}/fleet/areas.json"))
for a in ar["areas"]:
    a["area_id"], a["name"] = AM[a["area_id"]]; a["center"]["lat"] += 0.5
    a["asset_ids"] = [f"WELL-{int(x[5:]) + 200:04d}" for x in a["asset_ids"]]
json.dump(ar, open(f"{dst}/fleet/areas.json", "w"), indent=1)
for d in glob.glob(f"{src}/assets/*"):
    nd = f"{dst}/assets/WELL-{int(os.path.basename(d)[5:]) + 200:04d}"
    for p in glob.glob(d + "/**/*", recursive=True):
        if os.path.isdir(p): continue
        rel = ren(os.path.relpath(p, d)); os.makedirs(os.path.dirname(f"{nd}/{rel}"), exist_ok=True)
        t = ren(open(p).read())
        if rel == "metadata.json": m = json.loads(t); m["location"]["lat"] += 0.5; t = json.dumps(m, indent=1)
        open(f"{nd}/{rel}", "w").write(t)
print("wrote", len(os.listdir(f"{dst}/assets")), "wells to", dst)
