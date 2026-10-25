"""Layouts, villagers and dialogue for each map."""
import math

PI = math.pi
NORTH, SOUTH, WEST, EAST = 0.0, PI, PI / 2, -PI / 2  # yaw values for "facing" a direction

# CharacterModel enums
HAT = {"none": 0, "cap": 1, "top": 2, "beanie": 3, "straw": 4, "wizard": 5, "bow": 6}
EARS = {"none": 0, "bunny": 1, "cat": 2, "bear": 3}

SKIN = [(1.0, 0.84, 0.7), (0.96, 0.74, 0.56), (0.78, 0.55, 0.38), (0.55, 0.37, 0.25), (1.0, 0.9, 0.8)]


def look(skin=0, shirt=(0.9, 0.4, 0.4), pants=(0.3, 0.4, 0.7), shoes=(0.35, 0.22, 0.15), hair=(0.4, 0.25, 0.15),
         hat="none", hat_color=(0.9, 0.3, 0.3), ears="none", ear_color=None, has_hair=True):
    return {
        "skin_color": SKIN[skin],
        "shirt_color": shirt,
        "pants_color": pants,
        "shoe_color": shoes,
        "has_hair": has_hair,
        "hair_color": hair,
        "hat": HAT[hat],
        "hat_color": hat_color,
        "ears": EARS[ears],
        "ear_color": ear_color or hair,
    }


# ---------------------------------------------------------------------------
# Meadow Village: the hub. A cosy plaza with a fountain, houses, a farm,
# a windmill on the hill and a fishing pond. Portals lead to the other maps.
# ---------------------------------------------------------------------------

def meadow_village(Level):
    terrain = dict(
        size=160, seed_offset=1.3, base_height=3.0, amplitude=1.6, frequency=0.035,
        border_width=20, border_height=20,
        flats=[(0, 0, 28, 2.5), (32, 32, 13, -1.8), (0, -54, 10, 3.0), (54, 0, 10, 3.0), (-54, 0, 10, 3.0),
               (-32, 30, 15, 3.0), (-34, -30, 14, 6.0)],
        paths=[(0, -4, 0, -56), (4, 0, 56, 0), (-4, 0, -56, 0), (3, 3, 23, 23), (-3, 3, -26, 24),
               (-6, -24, -30, -28)],
        path_width=2.2,
        grass_color=(0.47, 0.74, 0.34), grass_alt_color=(0.4, 0.66, 0.31), sand_height=0.35, snow_height=40.0,
    )
    env = dict(sky_top=(0.3, 0.58, 0.95), sky_horizon=(0.72, 0.87, 0.98), ground=(0.42, 0.6, 0.4),
               fog=(0.75, 0.87, 0.97), fog_density=0.0035, sun_energy=1.15, sun_pitch=-0.95, sun_yaw=0.7)
    L = Level("meadow_village", terrain, env, water={"level": 0.0}, seed=11)

    L.reserve(0, 0, 6)
    L.place("fountain", 0, 0, group="Village", r=3.0)
    # Houses ring the plaza, doors facing the fountain.
    houses = ["house_red", "house_blue", "house_teal", "house_orange", "house_purple", "house_red", "house_blue", "house_teal"]
    for i, ang in enumerate([-150, -120, -60, -30, 22, 68, 100, 160]):
        a = math.radians(ang)
        x, z = math.cos(a) * 18, math.sin(a) * 18
        L.place(houses[i], x, z, L.face(x, z, 0, 0), group="Village", r=3.4)
    for x in (-5.5, 5.5):
        z = -27
        L.place("house_tall_red" if x < 0 else "house_tall_blue", x, z, L.face(x, z, 0, z), group="Village", r=3.4)
    # Plaza furniture.
    for i in range(4):
        a = math.radians(45 + i * 90)
        x, z = math.cos(a) * 6, math.sin(a) * 6
        L.place("bench", x, z, L.face(x, z, 0, 0) + PI, group="Village", r=1.0)
    L.ring("lamp_post", 0, 0, 11, 8, "Village", start=math.radians(22.5), r=0.5)
    for (x, z) in [(3, -21), (-3, -38), (22, 3), (38, -3), (-22, -3), (-38, 3)]:
        L.place("lamp_post", x, z, group="Village", r=0.5)
    L.place("market_stall_red", -7, 10, L.face(-7, 10, 0, 0), group="Village", r=2.0)
    L.place("market_stall_blue", 7.5, 9.5, L.face(7.5, 9.5, 0, 0), group="Village", r=2.0)
    for (x, z) in [(-9, 11.5), (-5, 12), (9.5, 11), (5.8, 11.8)]:
        L.place(["crate", "barrel"][int(x) % 2], x, z, x * 0.3, group="Village", r=0.6)
    L.place("well", 10, -9, group="Village", r=1.3)
    for (x, z) in [(-12, 4), (12, 4), (-4, 13.5), (4, -13.5), (-13, -5), (14, -3)]:
        L.place("flowers_pink" if x > 0 else "flowers_yellow", x, z, x, group="Village")
    L.sign(4, -6, "Village Square", [
        "Meadow Village: population cosy.",
        "North road → Whispering Woods",
        "East road → Sunny Shores",
        "West road → Frosty Peaks",
    ], (0, 0))

    # Windmill on the hill.
    L.place("windmill", -34, -30, L.face(-34, -30, -20, -22), group="Village", r=4.0)
    L.place("hay_bale", -29, -25, 0.4, group="Farm", r=1.0)
    L.place("hay_bale", -31, -24, 1.4, group="Farm", r=1.0)

    # A little fenced farm full of pumpkins.
    fx, fz = -32, 30
    for i in range(7):
        L.place("fence", fx - 7 + i * 2.2 + 1.1, fz - 6, 0, group="Farm", r=0.3)
        L.place("fence", fx - 7 + i * 2.2 + 1.1, fz + 6, 0, group="Farm", r=0.3)
    for i in range(5):
        if i != 2:
            L.place("fence", fx + 7.7, fz - 4.4 + i * 2.2, PI / 2, group="Farm", r=0.3)
        L.place("fence", fx - 7.7, fz - 4.4 + i * 2.2, PI / 2, group="Farm", r=0.3)
    L.reserve(fx, fz, 7)
    for row in range(3):
        for col in range(5):
            L.place("pumpkin", fx - 4.5 + col * 2.2, fz - 3 + row * 3, row + col, scale=0.9 + (row * col % 3) * 0.15, group="Farm")
    L.place("hay_bale", fx + 9, fz + 4, 0.3, group="Farm", r=1.0)
    L.place("tree_apple", fx + 11, fz - 6, group="Farm", r=1.5)

    # Fishing pond with a rowboat.
    L.place("rowboat", 34, 35, 0.7, y=-0.25, group="Pond", r=2.0)
    L.place("bench", 24.5, 25, L.face(24.5, 25, 32, 32) + PI, group="Pond", r=1.0)
    L.place("barrel", 23, 26.6, group="Pond", r=0.5)

    # Portals and spawns.
    L.portal("whispering_woods", "from_village", 0, -56, 0.0, (0.55, 1.0, 0.6))
    L.portal("sunny_shores", "from_village", 56, 0, PI / 2, (1.0, 0.8, 0.4))
    L.portal("frosty_peaks", "from_village", -56, 0, PI / 2, (0.7, 0.85, 1.0))
    L.spawn("Default", 0, 13, NORTH)
    L.spawn("from_woods", 0, -49, SOUTH)
    L.spawn("from_shores", 49, 0, WEST)
    L.spawn("from_peaks", -49, 0, EAST)
    L.sign(3.5, -50, "North Road", ["To the Whispering Woods.", "Mind the mushrooms. They're friendly but nosy."], (0, -40))
    L.sign(50, 3.5, "East Road", ["To Sunny Shores.", "Sunscreen recommended."], (40, 0))
    L.sign(-50, -3.5, "West Road", ["To Frosty Peaks.", "Bring a scarf. Bring two."], (-40, 0))

    # Villagers.
    L.npc(dict(id="mayor_bun", name="Mayor Bun", wander=2.5, look=look(
        skin=4, shirt=(0.6, 0.4, 0.85), pants=(0.25, 0.2, 0.35), hat="top", hat_color=(0.25, 0.2, 0.3),
        ears="bunny", ear_color=(0.98, 0.98, 0.98), hair=(0.98, 0.98, 0.98)),
        lines=["Oh! A new face in Meadow Village! Welcome, welcome!",
               "I'm Mayor Bun. I keep the flowers watered and the gossip flowing.",
               "Our village sits right in the middle of everything. Hop through the glowing rings to visit the Woods, the Shores or the Peaks.",
               "Make friends wherever you go! A town is only as cosy as its neighbours."],
        repeat=["Met anyone new lately? Everyone around here has a story, you know."]), 3, 7)
    L.npc(dict(id="pip", name="Pip the Baker", wander=1.5, look=look(
        skin=1, shirt=(0.98, 0.95, 0.88), pants=(0.85, 0.55, 0.35), hat="cap", hat_color=(0.98, 0.98, 0.98), hair=(0.9, 0.6, 0.3)),
        lines=["Fresh buns! Well... not THAT kind of Bun. The Mayor gets touchy about it.",
               "I'm Pip. I bake for the whole valley.",
               "If you're heading up to Frosty Peaks, Professor Frost still owes me for three blueberry pies."],
        repeat=["Try the cinnamon swirl. It swirls."]), -4.5, 8.5)
    L.npc(dict(id="tomo", name="Old Tomo", wander=0.0, yaw=L.face(22.5, 27.5, 32, 32), look=look(
        skin=2, shirt=(0.25, 0.62, 0.6), pants=(0.4, 0.35, 0.3), hat="straw", hat_color=(0.95, 0.85, 0.5), hair=(0.85, 0.85, 0.85)),
        lines=["Shh... you'll scare the fish.",
               "Name's Tomo. Been fishing this pond for forty years.",
               "Biggest fish I ever saw lives in there. Calls himself Gerald. Well, I call him Gerald.",
               "Captain Coral down at Sunny Shores says Gerald is a sea fish. Captain Coral is wrong."],
        repeat=["Still no sign of Gerald. He's playing hard to get."]), 22.5, 27.5)
    L.npc(dict(id="luma", name="Luma", wander=9.0, look=look(
        skin=0, shirt=(0.4, 0.75, 0.95), pants=(0.95, 0.6, 0.3), hair=(1.0, 0.6, 0.25), ears="cat", ear_color=(1.0, 0.6, 0.25)),
        lines=["Tag! You're it! ...Oh, you're new. Hi! I'm Luma!",
               "Did you see the windmill on the hill? It never stops spinning. I tried to stop it once. Once.",
               "Ranger Hazel says the trees in the Whispering Woods talk at night. I wanna hear them!"],
        repeat=["Race you to the fountain! ...You didn't even run."]), -12, -10)
    L.npc(dict(id="gus", name="Guard Gus", wander=1.0, yaw=SOUTH, look=look(
        skin=3, shirt=(0.3, 0.45, 0.8), pants=(0.2, 0.25, 0.4), hat="cap", hat_color=(0.25, 0.35, 0.7), hair=(0.15, 0.1, 0.1)),
        lines=["Halt! Who goes th-- oh, it's just you. Carry on.",
               "The road north leads to the Whispering Woods. Stay on the path; the mushrooms there are... enthusiastic.",
               "I've guarded this road for six years. Nothing has ever happened. I'm very good at my job."],
        repeat=["All quiet on the northern front."]), 3, -40)

    # Nature.
    keep = [(0, 0, 25), (32, 32, 9), (-32, 30, 9), (-34, -30, 7)]
    L.scatter(["tree_round", "tree_round_light", "tree_apple", "tree_pine", "tree_round"], 110, "Trees", r=1.8,
              scale=(0.85, 1.35), keep_out=keep, path_gap=2.0)
    L.scatter(["bush", "bush_berries"], 35, "Plants", r=0.8, scale=(0.8, 1.3), keep_out=keep[:1])
    L.scatter("rock", 18, "Rocks", r=1.2, scale=(0.6, 1.6), keep_out=keep[:1])
    L.scatter(["flowers_pink", "flowers_yellow", "flowers_purple", "flowers_white"], 60, "Plants", r=0.4, keep_out=keep[:1], path_gap=0.8)
    L.scatter("grass_tuft", 160, "Plants", register=False, path_gap=0.5, scale=(0.8, 1.4))
    for i in range(10):
        a = i * math.tau / 10 + 0.3
        L.place("cloud" if i % 2 else "cloud_big", math.cos(a) * 55, math.sin(a) * 55, a, y=34 + (i % 3) * 5, group="Sky")
    return L


# ---------------------------------------------------------------------------
# Whispering Woods: a dense forest with a stream, a ranger's cabin in a
# clearing, a giant-mushroom grove and a quiet pond.
# ---------------------------------------------------------------------------

def whispering_woods(Level):
    terrain = dict(
        size=160, seed_offset=4.1, base_height=3.6, amplitude=2.4, frequency=0.045,
        border_width=20, border_height=24,
        flats=[(0, 0, 22, 3.0), (0, 52, 10, 3.0), (-26, -22, 12, -1.6), (30, -26, 15, 3.5),
               (0, 19, 7, 3.0), (0, 39, 7, 3.0)],
        channels=[(-80, 37, -30, 26), (-30, 26, 10, 30), (10, 30, 80, 22)],
        channel_width=7.0, channel_bottom=-1.2,
        paths=[(0, 52, 0, 4), (4, -2, 28, -24), (-4, -3, -18, -15)],
        path_width=1.8,
        grass_color=(0.36, 0.64, 0.3), grass_alt_color=(0.3, 0.55, 0.28), path_color=(0.62, 0.46, 0.3),
        rock_color=(0.5, 0.5, 0.48), sand_color=(0.6, 0.55, 0.38), sand_height=0.3, snow_height=40.0,
    )
    env = dict(sky_top=(0.38, 0.6, 0.85), sky_horizon=(0.7, 0.85, 0.8), ground=(0.3, 0.45, 0.3),
               fog=(0.62, 0.8, 0.7), fog_density=0.009, sun_energy=1.0, sun_pitch=-1.0, sun_yaw=0.3,
               sun_color=(1.0, 0.95, 0.82))
    L = Level("whispering_woods", terrain, env, water={"level": 0.0, "color": (0.35, 0.68, 0.7), "deep": (0.2, 0.45, 0.55)}, seed=22)

    # Clearing with the ranger's cabin and a campfire.
    L.place("log_cabin", -9, -9, L.face(-9, -9, 0, 0), group="Camp", r=4.2)
    L.place("campfire", 3, 2, group="Camp", r=1.0)
    L.place("log_fallen", 3, 5, 0.1, group="Camp", r=1.0)
    L.place("log_fallen", 6.4, 1.2, PI / 2 + 0.2, group="Camp", r=1.0)
    L.place("stump", -0.5, 4.5, group="Camp", r=0.6)
    L.place("tent", 11, -5, L.face(11, -5, 3, 2), group="Camp", r=2.2)
    L.place("crate", -4.5, -11.5, 0.3, group="Camp", r=0.6)
    L.place("barrel", -3.5, -12.6, group="Camp", r=0.5)
    L.place("lamp_post", -3, -5, group="Camp", r=0.4)
    L.sign(3, 12, "Ranger Station", ["Whispering Woods Ranger Station.", "Please do not feed the mushrooms."], (0, 25))

    # Bridge over the stream.
    bridge_y = 2.95  # deck top sits flush with the flattened banks (3.0)
    L.place("bridge", 0, 29, 0.0, y=bridge_y, group="Camp", r=2.0)

    # Giant mushroom grove.
    L.scatter(["mushroom_red", "mushroom_blue"], 14, "Mushrooms", r=1.6, scale=(0.9, 2.3), area=((30, -26), 13), path_gap=0.8)
    L.scatter(["mushroom_red", "mushroom_blue"], 30, "Mushrooms", r=0.5, scale=(0.25, 0.45), path_gap=0.3)
    L.sign(20, -15, "Mushroom Grove", ["Mushroom Grove.", "Population: Kevin, and roughly four hundred of his friends."], (10, -8))

    # Pond.
    L.place("log_fallen", -15, -12, 0.8, group="Pond", r=1.2)
    L.place("rock", -33, -14, 1.0, scale=1.3, group="Pond", r=1.5)

    L.portal("meadow_village", "from_woods", 0, 56, 0.0, (1.0, 0.85, 0.5))
    L.spawn("Default", 0, 48, NORTH)
    L.spawn("from_village", 0, 48, NORTH)

    L.npc(dict(id="hazel", name="Ranger Hazel", wander=2.0, look=look(
        skin=1, shirt=(0.45, 0.55, 0.3), pants=(0.45, 0.35, 0.25), hat="cap", hat_color=(0.3, 0.5, 0.3), hair=(0.55, 0.3, 0.15)),
        lines=["Shh... listen. Hear that? That's the woods whispering.",
               "I'm Hazel, the ranger. I look after everything that grows out here.",
               "If you find the giant mushrooms, please don't poke them. They sneeze.",
               "And watch the stream. The bridge is safe. The stepping stones are... optimistic."],
        repeat=["The trees say hello. Well, they rustle. I choose to hear hello."]), -4, -3)
    L.npc(dict(id="moss", name="Moss", wander=4.0, look=look(
        skin=0, shirt=(0.6, 0.45, 0.3), pants=(0.35, 0.45, 0.3), hat="wizard", hat_color=(0.85, 0.3, 0.3), hair=(0.3, 0.2, 0.12)),
        lines=["Mushrooms! Mushrooms everywhere! Isn't it wonderful?",
               "I'm Moss. I've named every single mushroom in these woods.",
               "That big one's Kevin. The blue one is also Kevin. I ran out of names."],
        repeat=["Kevin says hi. Both Kevins."]), 27, -22)
    L.npc(dict(id="bramble", name="Bramble", wander=0.0, yaw=L.face(5, 4.6, 3, 2), look=look(
        skin=2, shirt=(0.85, 0.5, 0.3), pants=(0.4, 0.3, 0.25), hair=(0.45, 0.3, 0.18), ears="bear", ear_color=(0.45, 0.3, 0.18)),
        lines=["Mmm, nothing beats a campfire. Pull up a log.",
               "I'm Bramble. I tell stories. Want one? Once upon a time, there was a bear who wanted to be a baker...",
               "...he asked Pip for a job, and Pip said no. The end.",
               "It's a sad story. I'm working on a sequel."],
        repeat=["The sequel is called 'Bear Bakes Anyway'. It's a thriller."]), 5.2, 4.6)
    L.npc(dict(id="wisp", name="Wisp", wander=1.5, look=look(
        skin=4, shirt=(0.55, 0.45, 0.85), pants=(0.3, 0.25, 0.5), hat="wizard", hat_color=(0.4, 0.3, 0.7), hair=(0.85, 0.85, 1.0)),
        lines=["Oh! You can see me? How delightful.",
               "This pond remembers everyone who looks into it. Smile nicely.",
               "They say the glowing rings were here long before the village. I believe them. I was here too, after all."],
        repeat=["The pond says you have a kind face."]), -16.5, -13)

    keep = [(0, 0, 17), (30, -26, 10), (0, 29, 7)]
    L.scatter(["tree_pine", "tree_pine", "tree_round", "tree_round_light", "tree_autumn"], 210, "Trees", r=1.6,
              scale=(0.9, 1.6), keep_out=keep, path_gap=1.6)
    L.scatter(["bush", "bush_berries"], 50, "Plants", r=0.8, scale=(0.8, 1.4), keep_out=keep[:1])
    L.scatter(["log_fallen", "stump"], 16, "Plants", r=1.5, keep_out=keep[:1])
    L.scatter("rock", 22, "Rocks", r=1.2, scale=(0.6, 1.8))
    L.scatter(["flowers_white", "flowers_purple"], 40, "Plants", r=0.4, path_gap=0.6)
    L.scatter("grass_tuft", 180, "Plants", register=False, path_gap=0.4, scale=(0.9, 1.6))
    for i in range(6):
        a = i * math.tau / 6 + 0.8
        L.place("cloud_big", math.cos(a) * 60, math.sin(a) * 60, a, y=40 + (i % 2) * 6, group="Sky")
    L.extras.append(("leaves", {"name": "Fireflies", "amount": 120, "color": (1.0, 0.95, 0.5), "size": 0.05,
                                "gravity": 0.05, "height": 1.5, "lifetime": 6.0}))
    return L


# ---------------------------------------------------------------------------
# Sunny Shores: grassy hills rolling down to a sandy beach and the open sea,
# with a dock, beach huts and a lighthouse out on the headland.
# ---------------------------------------------------------------------------

def sunny_shores(Level):
    terrain = dict(
        size=160, seed_offset=2.6, base_height=1.4, amplitude=1.1, frequency=0.04, tilt=(0.0, -0.075),
        border_width=20, border_height=20, border_sides=(1, 1, 1, 0),
        flats=[(0, -52, 10, 5.4), (48, 20, 14, 5.0), (-30, -22, 12, 3.6), (14, -16, 10, 2.6)],
        paths=[(0, -52, 0, -12), (0, -12, -10, 8), (0, -12, 38, 12), (38, 12, 47, 18), (0, -24, -26, -22), (0, -12, 12, -15)],
        path_width=2.0,
        grass_color=(0.52, 0.82, 0.38), grass_alt_color=(0.46, 0.76, 0.35), sand_height=1.7,
        sand_color=(0.98, 0.9, 0.62), path_color=(0.9, 0.78, 0.55), snow_height=40.0,
    )
    env = dict(sky_top=(0.2, 0.55, 0.98), sky_horizon=(0.7, 0.9, 1.0), ground=(0.5, 0.65, 0.75),
               fog=(0.75, 0.9, 1.0), fog_density=0.0025, sun_energy=1.25, sun_pitch=-0.85, sun_yaw=2.6,
               sun_color=(1.0, 0.95, 0.82))
    L = Level("sunny_shores", terrain, env, water={"level": 0.0, "color": (0.25, 0.75, 0.95), "deep": (0.1, 0.45, 0.85), "size": 500},
              bounds=(-66, 66, -66, 34), seed=33)

    # Dock out into the sea, starting where the beach meets the water.
    z0 = next(z / 4 for z in range(0, 160) if L.h(-10, z / 4) < 0.45)
    L.place("dock", -10, z0 - 1.5, 0.0, y=0.55, group="Harbour", r=0)
    for z in range(int(z0 - 2), int(z0 + 16)):
        L.reserve(-10, z, 1.8)
    L.place("rowboat", -6.2, z0 + 11, 0.2, y=-0.3, group="Harbour")
    L.place("crate", -9, z0 + 1.5, 0.3, y=0.65, group="Harbour")
    L.place("barrel", -11.1, z0 + 2.3, y=0.65, group="Harbour")

    # Lighthouse on the headland.
    L.place("lighthouse", 51, 23, PI * 0.8, group="Harbour", r=3.0)
    L.place("bench", 45, 25, L.face(45, 25, 45, 40), group="Harbour", r=1.0)

    # Beach huts and a smoothie stand up the slope.
    for (x, z, kind) in [(-30, -22, "house_teal"), (-21, -25, "house_orange"), (14, -16, "house_purple")]:
        L.place(kind, x, z, L.face(x, z, x * 0.6, 10), group="Huts", r=3.4)
    L.place("market_stall_blue", 9, -4, L.face(9, -4, 0, 10), group="Huts", r=2.0)
    L.place("lamp_post", 3, -14, group="Huts", r=0.4)
    L.place("lamp_post", -3, -28, group="Huts", r=0.4)
    L.sign(3.5, -46, "Sunny Shores", ["Welcome to Sunny Shores!", "Swim between the flags. There are no flags. Swim carefully."], (0, -30))

    # Beach fun.
    for (x, z, kind) in [(-22, 9, "umbrella_red"), (-1, 10, "umbrella_yellow"), (20, 8, "umbrella_blue"), (28, 3, "umbrella_red")]:
        L.place(kind, x, z, x, group="Beach", r=1.6)
    L.place("sandcastle", 4, 13, 0.4, group="Beach", r=1.0)
    L.place("beach_ball", -18, 12, group="Beach")
    L.scatter(["starfish_orange", "starfish_pink"], 18, "Beach", r=0.3, min_h=0.05, max_h=1.2, path_gap=0.2, y_off=0.0)
    L.scatter("tree_palm", 26, "Trees", r=1.6, scale=(0.9, 1.3), min_h=0.6, max_h=2.6)
    L.scatter(["tree_round", "tree_round_light", "tree_palm"], 45, "Trees", r=1.8, scale=(0.9, 1.3), min_h=3.0,
              keep_out=[(48, 20, 9)])
    L.scatter("rock", 20, "Rocks", r=1.0, scale=(0.6, 1.8), min_h=-0.6, max_h=1.0, path_gap=0.5)
    L.scatter(["bush", "flowers_yellow", "flowers_pink"], 40, "Plants", r=0.6, min_h=2.5)
    L.scatter("grass_tuft", 120, "Plants", register=False, min_h=2.2, path_gap=0.5)

    L.portal("meadow_village", "from_shores", 0, -56, 0.0, (0.55, 1.0, 0.6))
    L.spawn("Default", 0, -48, SOUTH)
    L.spawn("from_village", 0, -48, SOUTH)

    L.npc(dict(id="captain_coral", name="Captain Coral", wander=0.0, yaw=NORTH, look=look(
        skin=2, shirt=(0.95, 0.95, 0.98), pants=(0.15, 0.2, 0.45), hat="cap", hat_color=(0.15, 0.2, 0.45), hair=(0.9, 0.9, 0.9)),
        lines=["Ahoy, landlubber! Welcome to Sunny Shores!",
               "Captain Coral's the name. This dock is my ship. It doesn't float, but it's never sunk either.",
               "Old Tomo still going on about Gerald? Gerald is a SEA fish. I'd know. He's my cousin's fish."],
        repeat=["Fair winds, matey! Or at least, mild breezes."]), -10, z0 + 13, 0.75)
    L.npc(dict(id="sunny", name="Sunny", wander=2.0, look=look(
        skin=1, shirt=(1.0, 0.55, 0.3), pants=(0.25, 0.7, 0.75), hat="straw", hat_color=(0.98, 0.88, 0.55), hair=(0.98, 0.85, 0.45)),
        lines=["Duuude. Feel that sun? Totally radical.",
               "I'm Sunny. Yeah, like the beach. My parents had one idea and they ran with it.",
               "If you ever wanna learn to surf, come back tomorrow. I say that every day."],
        repeat=["Waves are lookin' gnarly today. Gnarly means good. I think."]), -2, 6.5)
    L.npc(dict(id="wren", name="Keeper Wren", wander=1.5, look=look(
        skin=0, shirt=(1.0, 0.82, 0.25), pants=(0.25, 0.3, 0.45), hat="beanie", hat_color=(0.9, 0.3, 0.3), hair=(0.3, 0.2, 0.15)),
        lines=["Welcome to my lighthouse! Every night I light the lamp so the boats find their way home.",
               "From the top you can almost see Frosty Peaks. Almost. I squint a lot.",
               "Hundred and twelve steps to the top. I counted. Then I counted again and got a hundred and fourteen."],
        repeat=["The lamp's polished and ready. Shiny!"]), 45, 18)
    L.npc(dict(id="shelly", name="Shelly", wander=6.0, look=look(
        skin=3, shirt=(1.0, 0.6, 0.75), pants=(0.98, 0.95, 0.6), hat="bow", hat_color=(1.0, 0.45, 0.6), hair=(0.2, 0.12, 0.1)),
        lines=["Look! A shell shaped like a shell!",
               "I'm Shelly. I'm collecting one of every shell on the beach.",
               "I've got two so far. It's going great."],
        repeat=["Three shells now! ...Wait, that one's a rock."]), 10, 5)
    L.npc(dict(id="finn", name="Finn the Lifeguard", wander=1.0, yaw=SOUTH, look=look(
        skin=2, shirt=(0.92, 0.25, 0.25), pants=(0.95, 0.85, 0.3), hat="cap", hat_color=(0.95, 0.85, 0.3), hair=(0.15, 0.1, 0.08)),
        lines=["No running near the water! ...Unless it's a fun run. Then it's fine.",
               "I'm Finn. Lifeguard. I've been on duty for five years.",
               "Nobody's ever needed saving. Mostly I rescue sandcastles from the waves."],
        repeat=["Hydrate! Hydrate! Hydrate!"]), 18, 11)
    for i in range(8):
        a = i * math.tau / 8 + 0.2
        L.place("cloud" if i % 2 else "cloud_big", math.cos(a) * 60, math.sin(a) * 60, a, y=36 + (i % 3) * 5, group="Sky")
    return L


# ---------------------------------------------------------------------------
# Frosty Peaks: snowy hills ringed by mountains, an igloo camp, a frozen lake,
# a snowman field and a lookout plateau with glowing crystals.
# ---------------------------------------------------------------------------

def frosty_peaks(Level):
    terrain = dict(
        size=160, seed_offset=7.7, base_height=3.0, amplitude=4.5, frequency=0.04,
        border_width=22, border_height=30,
        flats=[(52, 0, 10, 3.0), (-20, 20, 18, -1.2), (24, -22, 16, 4.0), (-30, -34, 22, 11.0), (2, 4, 12, 2.5)],
        paths=[(52, 0, 30, -16), (52, 0, 4, 4), (4, 4, -8, 9), (-2, 0, -22, -24)],
        path_width=2.0,
        grass_color=(0.9, 0.93, 0.98), grass_alt_color=(0.8, 0.86, 0.96), rock_color=(0.55, 0.6, 0.7),
        path_color=(0.78, 0.84, 0.94), sand_color=(0.85, 0.92, 1.0), sand_height=-10.0, snow_height=100.0, rock_slope=0.45,
    )
    env = dict(sky_top=(0.45, 0.6, 0.9), sky_horizon=(0.85, 0.9, 0.98), ground=(0.8, 0.85, 0.95),
               fog=(0.78, 0.85, 0.96), fog_density=0.005, sun_energy=0.8, sun_pitch=-0.6, sun_yaw=-0.5,
               sun_color=(1.0, 0.9, 0.8), ambient=(0.75, 0.82, 1.0), ambient_energy=0.55, saturation=1.1)
    L = Level("frosty_peaks", terrain, env, water=None, seed=44)

    # Frozen lake (walkable ice).
    L.place("ice_sheet", -20, 20, scale=14, y=-0.6, group="Lake", r=0)
    L.reserve(-20, 20, 11)
    L.place("sled", -10, 13, 0.6, group="Lake")

    # Igloo camp.
    for (x, z) in [(20, -28), (31, -22), (18, -15)]:
        L.place("igloo", x, z, L.face(x, z, 24, -22), group="Camp", r=3.0, y_off=-0.1)
    L.place("campfire", 24, -21, group="Camp", r=1.0)
    L.place("log_fallen", 26.5, -19, 0.6, group="Camp", r=1.0)
    L.place("crystal_blue", 29, -29, 0.4, group="Camp", r=1.0)
    L.place("crystal_pink", 32, -27, 1.4, scale=0.8, group="Camp", r=1.0)
    L.place("crate", 14, -22, 0.3, group="Camp", r=0.6)
    L.sign(44, -4, "Frosty Peaks", ["Welcome to Frosty Peaks!", "Igloo camp: south-west.", "Frozen lake: west.", "Lookout: way up there."], (52, 0))

    # Snowman field.
    for i, (x, z) in enumerate([(-2, 1), (6, 8), (8, -2), (-4, 9), (12, 4)]):
        L.place("snowman", x, z, L.face(x, z, 2, 4) + PI, group="Snowmen", r=1.0)

    # Lookout plateau with crystals.
    L.scatter(["crystal_blue", "crystal_pink"], 9, "Crystals", r=1.2, scale=(0.8, 1.6), area=((-30, -34), 10), path_gap=0.5, max_slope=2)
    L.place("bench", -30, -30, L.face(-30, -30, -30, 0), group="Crystals", r=1.0)
    L.sign(-25, -27, "Peak Lookout", ["Peak Lookout.", "On a clear day you can see the whole valley.", "Today is a cloudy day."], (-10, -12))

    # Distant mountains for the skyline.
    for i in range(14):
        a = i * math.tau / 14 + 0.1
        L.place("mountain_snow", math.cos(a) * 95, math.sin(a) * 95, a, scale=1.0 + (i % 3) * 0.35, y=8, group="Mountains")

    L.portal("meadow_village", "from_peaks", 56, 0, PI / 2, (0.55, 1.0, 0.6))
    L.spawn("Default", 48, 0, WEST)
    L.spawn("from_village", 48, 0, WEST)

    L.npc(dict(id="yuki", name="Yuki", wander=2.5, look=look(
        skin=0, shirt=(0.6, 0.8, 1.0), pants=(0.3, 0.35, 0.6), hat="beanie", hat_color=(0.35, 0.55, 0.95), hair=(0.15, 0.1, 0.1)),
        lines=["Brrr! Welcome to Frosty Peaks! Want to see my igloo? It's very... cool.",
               "I'm Yuki. I build igloos. Igloo number six is my masterpiece.",
               "Igloos one through five? We don't talk about igloos one through five."],
        repeat=["Thinking about igloo number seven. Two floors. Maybe a slide."]), 22, -18)
    L.npc(dict(id="professor_frost", name="Professor Frost", wander=1.5, look=look(
        skin=4, shirt=(0.75, 0.78, 0.85), pants=(0.3, 0.3, 0.38), hat="top", hat_color=(0.2, 0.22, 0.3), hair=(0.95, 0.95, 0.98)),
        lines=["Ah, a visitor! Have you come to see my crystals? They glow, you know. Science!",
               "I'm Professor Frost. I study the ice crystals up here. They hum when it snows.",
               "Oh, and if you see Pip, tell them the pies are... still being researched. Thoroughly."],
        repeat=["Fascinating! This crystal is 3% sparklier than yesterday."]), 29, -25.5)
    L.npc(dict(id="pebble", name="Pebble", wander=5.0, look=look(
        skin=1, shirt=(0.95, 0.4, 0.4), pants=(0.35, 0.45, 0.75), hair=(0.98, 0.98, 1.0), ears="bear", ear_color=(0.98, 0.98, 1.0)),
        lines=["I built ALL these snowmen! Well, most of them. Okay, one.",
               "That one's Mr. Carrots. Say hi to Mr. Carrots.",
               "...He said hi back. I heard it."],
        repeat=["Mr. Carrots wants to know if you've got any spare buttons."]), 3, 6)
    L.npc(dict(id="bjorn", name="Old Bjorn", wander=1.0, yaw=L.face(-8, 9, -20, 20), look=look(
        skin=2, shirt=(0.55, 0.3, 0.25), pants=(0.3, 0.28, 0.3), hat="beanie", hat_color=(0.55, 0.4, 0.3), hair=(0.85, 0.85, 0.85)),
        lines=["This lake has been frozen for a hundred years. I've been skating on it for ninety.",
               "Mind your step. Ice is slippery. That's its whole job.",
               "Down in Meadow Village they say the windmill turns all by itself. I say it's showing off."],
        repeat=["Hrmph. Lovely weather. For a snowman."]), -7, 8)

    keep = [(-20, 20, 15), (24, -22, 11), (2, 4, 10), (-30, -34, 12)]
    L.scatter(["tree_pine_snow", "tree_pine_snow", "tree_pine"], 120, "Trees", r=1.7, scale=(0.9, 1.6), keep_out=keep, path_gap=1.8, min_h=-5)
    L.scatter(["rock_snow", "bush_snow"], 40, "Rocks", r=1.0, scale=(0.6, 1.6), keep_out=keep[:3], min_h=-5)
    L.extras.append(("snow", {"amount": 700}))
    return L


LEVELS = [meadow_village, whispering_woods, sunny_shores, frosty_peaks]
