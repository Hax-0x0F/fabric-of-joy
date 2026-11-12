execute as @a[tag=!fab.seen] run function fabryka:joined
execute as @a[scores={fab.left=1..}] run function fabryka:joined
# Shown 3 s after joining, below the join messages of other mods.
scoreboard players remove @a[scores={fab.delay=1..}] fab.delay 1
execute as @a[scores={fab.delay=1}] run function fabryka:show
# /trigger klawisze shows the hints; /trigger klawisze set -1 stops showing them on join.
scoreboard players enable @a klawisze
execute as @a[scores={klawisze=1..}] run function fabryka:show
execute as @a[scores={klawisze=..-1}] run scoreboard players set @s fab.hide 1
execute as @a[scores={klawisze=..-1}] run tellraw @s {"translate":"fabryka.keys.hidden","fallback":"Podpowiedzi wyłączone. Przywrócisz je: /trigger klawisze","color":"gray"}
scoreboard players set @a[scores={klawisze=..-1}] klawisze 0
scoreboard players set @a[scores={klawisze=1..}] klawisze 0
