import flet as ft
import re
import textwrap

characters = {
    "ME": "Detective",
    "CT": "Count Traffikson",
    "DS": "Doctor Simoal",
    "LB": "Lady Backmeth",
    "LD": "Little Dimmy",
}

scenes = {
    # The Incident
    ("Well", "10:00"): """LB seemingly kills LD""",
    ("Well", "10:08"): """DS finds LD and is devastated. Who could have done it?""",
    ("Well", "10:10"): """
        We arrive. DS asks us if we just arrived. No, we've been here all along.
        Then it must have been you! What?""",
    # The Revenge
    ("Tonton Coffee House", "11:55"): """DS plants TNT to kill us.""",
    ("Tonton Coffee House", "12:00"): """It kills LB. DS decides to kill us manually""",
    ("Tonton Coffee House", "12:13"): """We are late.""",
    ("Tonton Coffee House", "12:30"): """
        CT finds LB, is devastated. Finds that we were the only other reservation at 11:00""",
    # The Re-revenge
    ("Street", "13:50"): """CT hoists piano and watches watch.""",
    ("Street", "14:00"): """DS arrives to kill us. CT drops piano. Kills DS""",
    ("Street", "14:17"): """We are late. Police summons us.""",
    # The Case
    ("Scotland Yard", "16:25"): """
        We are late. LD survived! Police ask our help to find out who pushed him in the well.""",
    ## The Tools of the Trade
    ("Sandwich Manor", "21:31"): """
        I wanted to reach Sandwich Manor by 21:00, but events once again conspired against me.

        I entered the creepy manor and made my way to the hidden room beneath the stairs.
        I retrieved the Time Burrower from its box.
        It appeared to be an elaborate combination of a compass and a pocket watch.
        I learned about using it from an old wizard in Kabul.
        He taught me how it could be used to review events of the past, as long as I knew the time and place.

        I kept it hidden all these years. But the murder at noon has unrattled me so much,
        I had to invoke its powers today.
        """,
    ## The Reveal
    ("Scotland Yard", "22:35"): """
        "We expected to see you 35 minutes ago," the policeman grumbled when I entered the station.

        "Sorry I'm late," I said. "It builds up, you know? When I arrived at [Sandwich Manor] at 21:31 I was already 31 minutes late. I can never catch up."

        "No excuse. Well, can you tell us who committed the murder at the [Tonton Coffee House]?"

        "Yes, of course," I said, furiously searching my pockets with sweaty hands. "The murderer is..."
        """,
}
for k, v in scenes.items():
    v = textwrap.dedent(v)
    v = re.sub(r"\[(.*?)\]", lambda m: f"[{m.group(1)}]({m.group(1).replace(' ', '_')})", v)
    scenes[k] = v

def known_scenes_md():
    print("known_scenes_md")
    if known_scenes == {current_scene}:
        return ""
    texts = []
    last_loc = None
    for loc, time in sorted(known_scenes, key=lambda x: x[1]):
        if last_loc:
            texts.append("→")
        if loc != last_loc:
            texts.append(loc)
            last_loc = loc
        if (loc, time) == current_scene:
            texts.append(f"**{time}**")
        else:
            texts.append(f"[{time}]({loc.replace(' ', '_')}--{time})")
    print(current_scene, " ".join(texts))
    return " ".join(texts)

md_style_sheet = ft.MarkdownStyleSheet()

async def main(page: ft.Page):
    global current_scene, known_locations, known_scenes
    page.title = "Late for Murder"
    prefs = ft.SharedPreferences()
    current_scene = await prefs.get("current_scene")
    current_scene = tuple(current_scene) if current_scene else ("Scotland Yard", "22:35")
    known_locations = await prefs.get("known_locations")
    known_locations = set(known_locations) if known_locations else {current_scene[0]}
    known_scenes = await prefs.get("known_scenes")
    known_scenes = {tuple(ks.split("--")) for ks in known_scenes} if known_scenes else {current_scene}
    async def scene_tap_link(e):
        known_locations.add(e.data.replace("_", " "))
        await prefs.set("known_locations", sorted(known_locations))
        burrower_location.options = [ft.DropdownOption(kl) for kl in sorted(known_locations)]
    def use_burrower_clicked(e):
        use_burrower_btn.visible = False
        use_burrower_controls.visible = True
    async def burrower_go_clicked(e):
        global current_scene
        use_burrower_btn.visible = True
        use_burrower_controls.visible = False
        current_scene = burrower_location.value, burrower_time.value
        await prefs.set("current_scene", list(current_scene))
        location_label.value = current_scene[0]
        time_label.value = current_scene[1]
        if current_scene in scenes:
            scene_text_md.value = scenes[current_scene]
            known_scenes.add(current_scene)
            await prefs.set("known_scenes", sorted(f"{loc}--{time}" for (loc, time) in known_scenes))
        else:
            scene_text_md.value = "Nothing"
        timeline_md.value = known_scenes_md()
    async def timeline_click(e):
        global current_scene
        loc, time = e.data.split("--")
        loc = loc.replace("_", " ")
        current_scene = loc, time
        await prefs.set("current_scene", list(current_scene))
        location_label.value = loc
        time_label.value = time
        scene_text_md.value = scenes[current_scene]
        timeline_md.value = known_scenes_md()

    timeline_md = ft.Markdown(known_scenes_md(), on_tap_link=timeline_click)
    location_label = ft.Text(current_scene[0], size=25)
    time_label = ft.Text(current_scene[1], weight=ft.FontWeight.BOLD)
    scene_text_md = ft.Markdown(scenes[current_scene], on_tap_link=scene_tap_link, md_style_sheet=md_style_sheet)
    use_burrower_btn = ft.Button("Use Time Burrower", on_click=use_burrower_clicked)
    burrower_location = ft.Dropdown(label="Where", options=[ft.DropdownOption(kl) for kl in sorted(known_locations)])
    burrower_time = ft.TextField(label="When")
    burrower_go_btn = ft.Button("Burrow!", on_click=burrower_go_clicked)
    use_burrower_controls = ft.Row(visible=False, controls=[burrower_location, burrower_time, burrower_go_btn])

    page.add(timeline_md)
    page.add(ft.Divider())
    page.add(location_label)
    page.add(time_label)
    page.add(scene_text_md)
    page.add(use_burrower_btn)
    page.add(use_burrower_controls)


if __name__ == "__main__":
    ft.run(main)
