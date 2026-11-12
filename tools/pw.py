"""Minimal packwiz stand-in for a Modrinth-only pack: update, add, remove, check deps, refresh index.

pw.py PACK update SLUG [VERSION_ID]   newest Fabric 1.21.1 release (or the given version)
pw.py PACK add MODRINTH_SLUG SIDE     new mods/<slug>.pw.toml from the newest Fabric 1.21.1 release
pw.py PACK remove SLUG
pw.py PACK deps                       every required dependency of every pinned version is in the pack
pw.py PACK refresh                    rebuild index.toml (sha256) and pack.toml's index hash
"""
import glob, hashlib, json, os, re, sys, tomllib, urllib.parse, urllib.request

UA = {"User-Agent": "haxtistic/fabric-of-joy pack maintenance"}
Q = "?loaders=" + urllib.parse.quote('["fabric"]') + "&game_versions=" + urllib.parse.quote('["1.21.1"]')


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA)) as r:
        return json.load(r)


def write_pw(path, name, side, version):
    f = next((f for f in version["files"] if f["primary"]), version["files"][0])
    body = (
        f'name = {json.dumps(name, ensure_ascii=False)}\n'
        f'filename = {json.dumps(f["filename"], ensure_ascii=False)}\n'
        f'side = "{side}"\n\n'
        f'[download]\n'
        f'url = {json.dumps(f["url"], ensure_ascii=False)}\n'
        f'hash-format = "sha512"\n'
        f'hash = "{f["hashes"]["sha512"]}"\n\n'
        f'[update]\n[update.modrinth]\n'
        f'mod-id = "{version["project_id"]}"\n'
        f'version = "{version["id"]}"\n'
    )
    open(path, "w").write(body)
    print(f"{os.path.basename(path)}: {version['version_number']} ({f['filename']})")


def newest(project, channel_any=False):
    vs = get(f"https://api.modrinth.com/v2/project/{project}/version{Q}")
    rel = [v for v in vs if v["version_type"] == "release"] or (vs if channel_any else [])
    if not rel:
        sys.exit(f"{project}: no Fabric 1.21.1 release")
    return max(rel, key=lambda v: v["date_published"])


def update(pack, slug, version_id=None):
    path = f"{pack}/mods/{slug}.pw.toml"
    t = tomllib.load(open(path, "rb"))
    cur = get(f"https://api.modrinth.com/v2/version/{t['update']['modrinth']['version']}")
    if version_id:
        v = get(f"https://api.modrinth.com/v2/version/{version_id}")
    else:
        # Stay on the channel the pin is on: a beta pin may move to a newer beta.
        v = newest(t["update"]["modrinth"]["mod-id"], channel_any=cur["version_type"] != "release")
    write_pw(path, t["name"], t["side"], v)


def add(pack, project, side):
    p = get(f"https://api.modrinth.com/v2/project/{project}")
    write_pw(f"{pack}/mods/{p['slug']}.pw.toml", p["title"], side, newest(p["id"]))


def deps(pack):
    pinned = {}
    for f in glob.glob(f"{pack}/mods/*.pw.toml"):
        m = tomllib.load(open(f, "rb"))["update"]["modrinth"]
        pinned[m["mod-id"]] = m["version"]
    versions = get("https://api.modrinth.com/v2/versions?ids=" + urllib.parse.quote(json.dumps(list(pinned.values()))))
    names = {p["id"]: p["slug"] for p in get("https://api.modrinth.com/v2/projects?ids=" + urllib.parse.quote(json.dumps(list(pinned))))}
    ok = True
    for v in versions:
        for d in v["dependencies"]:
            if d["dependency_type"] == "required" and d.get("project_id") and d["project_id"] not in pinned:
                ok = False
                print(f"MISSING: {names.get(v['project_id'])} {v['version_number']} needs project {d['project_id']}")
            if d["dependency_type"] == "required" and d.get("version_id") and d["project_id"] in pinned and pinned[d["project_id"]] != d["version_id"]:
                print(f"note: {names.get(v['project_id'])} names version {d['version_id']} of {names.get(d['project_id'])}, pack pins {pinned[d['project_id']]}")
            if d["dependency_type"] == "incompatible" and d.get("project_id") in pinned:
                ok = False
                print(f"INCOMPATIBLE: {names.get(v['project_id'])} declares {names.get(d['project_id'])} incompatible")
    print("deps ok" if ok else "deps FAILED")


def refresh(pack, preserve):
    ignore = [l.strip() for l in open(f"{pack}/.packwizignore") if l.strip() and not l.startswith("#")]
    files = []
    for root, dirs, names in os.walk(pack):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for n in names:
            rel = os.path.relpath(os.path.join(root, n), pack)
            if rel in ("pack.toml", "index.toml") or n.startswith(".") or any(
                    rel == e.strip("/") or rel.startswith(e.strip("/") + "/") for e in ignore):
                continue
            files.append(rel)
    out = ['hash-format = "sha256"\n']
    for rel in sorted(files):
        h = hashlib.sha256(open(f"{pack}/{rel}", "rb").read()).hexdigest()
        out.append(f'\n[[files]]\nfile = {json.dumps(rel, ensure_ascii=False)}\nhash = "{h}"\n')
        if rel.endswith(".pw.toml"):
            out.append("metafile = true\n")
        if rel in preserve:
            out.append("preserve = true\n")
    open(f"{pack}/index.toml", "w").write("".join(out))
    h = hashlib.sha256(open(f"{pack}/index.toml", "rb").read()).hexdigest()
    pt = open(f"{pack}/pack.toml").read()
    pt = re.sub(r'(\[index\][^\[]*?hash = ")[0-9a-f]+(")', rf"\g<1>{h}\g<2>", pt, count=1, flags=re.S)
    open(f"{pack}/pack.toml", "w").write(pt)
    print(f"index: {len(files)} files, {len(preserve & set(files))} preserved")


if __name__ == "__main__":
    pack, cmd, *args = sys.argv[1:]
    if cmd == "update":
        for s in args:
            update(pack, s)
    elif cmd == "update-to":
        update(pack, args[0], args[1])
    elif cmd == "add":
        add(pack, args[0], args[1])
    elif cmd == "remove":
        os.remove(f"{pack}/mods/{args[0]}.pw.toml")
    elif cmd == "deps":
        deps(pack)
    elif cmd == "refresh":
        # Keep the preserve flags already in index.toml (as packwiz does), plus any paths given.
        old = tomllib.load(open(f"{pack}/index.toml", "rb"))
        preserve = {f["file"] for f in old.get("files", []) if f.get("preserve")} | set(args)
        refresh(pack, preserve)
