# The first five joins show the hints, unless the player turned them off.
tag @s add fab.seen
scoreboard players reset @s fab.left
scoreboard players add @s fab.joins 1
execute if score @s fab.joins matches ..5 unless score @s fab.hide matches 1 run scoreboard players set @s fab.delay 60
