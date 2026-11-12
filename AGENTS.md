# fabric-of-joy

A packwiz pack for Minecraft 1.21.1 on Fabric, played on the server "szyszki" (`szyszki.mc.tehom.eu`). `README.md` is for players: Polish, step by step, no technical terms. Everything for developers and agents goes here.

## Where it lives

- Source: `git.reprostar.pl/haxtistic/fabric-of-joy`. Gitea push-mirrors every push to the public `github.com/Hax-0x0F/fabric-of-joy`, overwriting it: changes made on GitHub are lost.
- The pack is public. Nothing secret goes in it (bot tokens, databases): the homelab keeps those in SOPS and renders them on the server.
- The server runs a pinned commit, set by `PACKWIZ_URL` in the homelab's `stacks/minecraft/compose.yaml.j2`. A change reaches the server only when the homelab moves that pin and deploys.

## Releases

- A tag `vX.Y.Z` matching `version` in `pack.toml` triggers `.github/workflows/release.yml` on GitHub (the job is skipped on Gitea). It checks `packwiz refresh` changes nothing, builds a `.mrpack` and a Prism instance (`launcher/prism/`, with packwiz-installer-bootstrap v0.0.3 checked by SHA-256), publishes the tagged tree on GitHub Pages and creates the release.
- The Prism instance installs from `https://hax-0x0f.github.io/fabric-of-joy/pack.toml` at every start, so players follow the latest release, not `main`.
- The `.mrpack` carries configs as overrides, which launchers may overwrite on update: `preserve` does not apply there.

## Files players own

Marked `preserve = true` in `index.toml`, so packwiz-installer writes them only when missing: `options.txt`, `servers.dat`, the JourneyMap minimap presets, `config/seasonhud-client.toml`, `config/enchdesc.json`, `config/voicechat/voicechat-client.properties`, `config/toughasnails/client.toml`. A change to them reaches new installs only. Server rules (Serene Seasons, Tough as Nails temperature and thirst) are not preserved.

- `options.txt` holds only the pack's choices and the key layout, where every key does one thing (Fabric gives one key to one binding). Minecraft fills in the rest.
- Never ship a player's own copy of these files, nor JourneyMap's `journeymap.core.config` or data, voice chat caches, Sodium's fingerprint or Controlify's device profiles.

## Key hints

`config/openloader/packs/fabryka-klawisze/` is a datapack and resource pack in one, loaded into every world by Open Loader. It prints the main keys with `{"keybind": id}`, which shows each player's own binding, on their first five joins; `/trigger klawisze` shows it again. Texts are in its `lang/` files.

## Changing mods

- Stay on Minecraft 1.21.1 unless every mod with world content has a build for the target version.
- Before an update, check that the mod id is unchanged (Hybrid Aquatic 1.6 renamed it, which would wipe its content from the world) and that every required dependency is in the pack.
- After any change, `packwiz refresh` and commit `index.toml` with it.
- Fabric Loader (`versions.fabric` in `pack.toml`) reaches players only through a new Prism instance: packwiz does not change
  the loader of an existing one. Move it only when a mod needs it or a release asks players to re-import anyway,
  and then to the newest stable loader (meta.fabricmc.net). Check each updated jar's `depends.fabricloader`.

## Docs

`AGENTS.md`, `CLAUDE.md` and `README.md` are in `.packwizignore`, with `.github/` and `launcher/`: they are not part of the pack.
