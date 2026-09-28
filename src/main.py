import flet as ft
import re
import textwrap

characters = {
    "ID": "Inspector Discorde",
    "CT": "Count Traffikson",
    "DS": "Doctor Simoal",
    "LB": "Lady Backmeth",
    "LD": "Little Dimmy",
    "GU": "Gustav",
}

_planning = {
    (0, "Scotland Yard", "22:35"): "final scene",
    (1, "Sandwich Manor", "21:31"): "pick up burrower",
    (2, "Scotland Yard", "20:29"): "ID tells us LD is alive",
    (3, "Little Dimmy"): "",
    (4, "Inspector Discorde"): "",
    (5, "Tonton Coffee House", "12:00"): "LB dies",
    (6, "Tonton Coffee House", "12:15"): "We arrive",
    (7, "Gustav"): "",
    (8, "Gasworks", "11:45"): "leave for restaurant",
    (9, "Marple House", "8:00"): "calling ",
    (10, "Marple House", "8:15"): "go to work ",
    (11, "Gasworks", "10:10"): "We arrive. DS accuses us.",
    (12, "Gasworks", "10:00"): "LB seemingly kills LD",
    (13, "Lady Backbeth"): "",
    (14, "Count Traffikson"): "",
    (15, "Gasworks", "10:08"): "DS finds LD and is devastated. Who could have done it?",
    (16, "Opera", "18:17"): "We are late. Police summons us.",
    (17, "Opera", "18:00"): "DS arrives to kill us. CT drops piano. Kills DS",
    (18, "Tonton Coffee House", "12:30"): "CT finds LB, is devastated. Finds that we were the only other reservation at 11:00",
    (19, "Opera", "17:50"): "CT hoists piano and watches watch.",
    (20, "Tonton Coffee House", "11:55"): "DS posions food to kill us.",
    (21, "Doctor Simoal"): "",
}

_deps = """
   0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21
 0 .  x  x        x
 1    .  x        x
 2       .  x  x  x
 3 LD       .                             x
 4 ID    ?     .  x                                ?
 5                .  x                       x
 6                   .  x  x  x
 7 GU                   .           ?  ?        ?
 8                         .
 9                            .  x
10                               .
11                                  .
12                                     .  x
13 LB                                     .  x
14 CT                                        .
15                                              .
16                                                 .
17                                                    .
18                                                       .
19                                                          .
20                                                             .
21 DS                                                             .
"""

scenes = {
    # The Morning
    ("Marple House", "8:00"): """
        I was about to leave for the [Gasworks] when I remembered something. I had to place a quick call to
        the [Tonton Coffee House] in Dampstead.

        "Hello, I'd like to make a reservation," I started. But on the end of the line, I only heard music.
        "I'm sorry, could you please turn down the music? Hello? Is this Tonton Coffee House? I can't hear
        you over the music. Can you hear me? Is there a dance party going on there? Please turn it down."

        This fruitless conversation went on for another 15 minutes before I was able to talk to the staff and
        reserve a table for 12:00. And now I was late for work!
        """,
    # The Incident
    ("Gasworks", "10:00"): """LB seemingly kills LD""",
    ("Gasworks", "10:08"): """DS finds LD and is devastated. Who could have done it?""",
    ("Gasworks", "10:10"): """
        We arrive. DS asks us if we just arrived. No, we've been here all along.
        Then it must have been you! What?""",
    ("Gasworks", "11:45"): """
        My four-hour shift at the Department of Kinetics and Magnetism was up.
        Then it must have been you! What?""",
    # The Revenge
    ("Tonton Coffee House", "11:55"): """DS posions food to kill us.""",
    ("Tonton Coffee House", "12:00"): """
        The front doors of the [Tonton Coffee House] swung wide open as [Lady Backmeth]
        walked in. As she got older, she made a point of following the latest fashion trends.
        She was dressed today in a fashionable striped black and white skirt, white blouse, and a
        wide-brimmed lace hat, to shield her from the glare of the sun on this early autumn day.

        LB: "I've arrived a little earlier than expected, [Gustav]. I hope it's no trouble?"
        she addressed the head waiter hurrying to lead her to her table.

        "No problem at all, my lady. This way, please. Will you have the usual?"

        LB: "Not today, [Gustav]. I want to try the goat cheese salad that [CT] raved about."

        "Of course."

        [Lady Backmeth] sat down. She read her magazine. Her lunch was served and consumed.

        LB: "Poison!" she croaked. [Gustav] called for help, but it was too late. [LB] was dead.

        Tragic. And I missed it all. I only arrived fifteen minutes later.
        """,
    ("Tonton Coffee House", "12:15"): """
        "Hello, I've placed a reservation for a table this morning," I informed the waiter.
        "My name's Marble." I spent

        "I don't see it on the reservation sheet," the man said. He flipped back to the previous page
        and there it was. "There it is! It was for 12:00, wasn't it?"

        Was I being chided by a waiter? There was no way to get here any sooner in this traffic!
        Half an hour all the way from the [Gasworks] was actually my best time yet. I must have given
        the waiter quite the glare, for he apologized.

        "I'm sorry, sir. We had a... busy day today," he said. Now that I know about the incident earlier,
        I am sure that is what he was referring to.

        DS: A man was looking at me! He had been hiding behind a large sheet of newspaper, sitting by the
        windows. I never noticed him before.

        DS: "So, Marble has dodged the proverbial bullet, has he not?" [DS] uttered and puffed on his cigar.
        "Let's see them dodge a literal bullet."
        """,
    ("Tonton Coffee House", "12:30"): """
        CT finds LB, is devastated. Finds that we were the only other reservation at 11:00""",
    # The Re-revenge
    ("Opera", "17:50"): """CT hoists piano and watches watch.""",
    ("Opera", "18:00"): """DS arrives to kill us. CT drops piano. Kills DS""",
    ("Opera", "18:17"): """We are late. Police summons us.""",
    # The Case
    ("Scotland Yard", "20:29"): """
        I arrived later than I intended. [ID] was not waiting for me at the entrance,
        but he had left instructions, and the constables directed me to his office.
        He started talking as soon as I entered.

        ID: "We have good news and bad news. The good news is that [Little Dimmy], the boy
        who fell into the well this morning, has been safely rescued," Inspector Discorde said
        as soon as I entered his office at the [Scotland Yard].

        "And the bad news?" I asked.

        ID: "The bad news is that we have no leads for the murder at the restaurant.
        No leads, except you. The victim was killed when she took your reserved table."

        I paled at the implication. I had to defend myself, and I knew just how I could do that.

        "Please, [ID]," I pleaded. "Allow me to clear my name. I have access to a mystical
        device that will allow me to scry the identity of the murderer."

        ID: "Very well, sir. I give you until 22:00 to consult the occult and come back to tell us the
        name of the murderer. Do not be late this time!"

        "I promise I won't be," I said and set out toward [Sandwich Manor], the abandoned mansion
        of a distant relative of mine.
        """,
    ## The Tools of the Trade
    ("Sandwich Manor", "21:31"): """
        I wanted to reach Sandwich Manor by 21:00, but events once again conspired against me.
        My carriage broke down, I was held up by news of marauding sea lions (false alarm, thank God!),
        and I got lost in the fog. In the end, my trip took twice as long as expected,
        but I finally made it all the way from the [Scotland Yard]. I did not look forward to making
        the same trek back.

        I entered the creepy manor and made my way to the hidden room beneath the stairs.
        I retrieved the **Time Burrower** from its dusty wooden box.
        It appeared to be an elaborate combination of a compass and a pocket watch.
        I learned about using it from an old wizard in Kabul.
        He taught me how it could be used to review events of the past, as long as I knew the time and place,
        and was familiar with the people involved.

        I had kept it hidden all these years. But the murder at noon has unrattled me so much,
        I had to invoke its powers today.
        """,
    ## The Reveal
    ("Scotland Yard", "22:35"): """
        ID: "We expected to see you 35 minutes ago," Inspector Discorde grumbled when I entered the station.

        "Sorry I'm late," I said. "It builds up, you know? When I arrived at [Sandwich Manor] at 21:31 I was already 31 minutes late. I can never catch up."

        ID: "No excuse. Well, can you tell us who committed the murder at the [Tonton Coffee House]?"

        "Yes, of course," I said, furiously searching my pockets with sweaty hands. "The murderer is..."
        """,
}


def get_scene_md(key):
    if key not in scenes:
        return "Nothing."
    v = scenes[key]
    v = textwrap.dedent(v)
    v = v.replace("\n\n", "PARAGRAPH").replace("\n", " ").replace("PARAGRAPH", "\n\n").strip()
    for s, n in characters.items():
        v = v.replace(f"[{s}]", f"[{n}]")
    for s, n in characters.items():
        if n not in known_characters:
            v = re.sub( f"^{s}: (.*)", lambda m: "█" * (len(m.group(1)) // 2), v, flags=re.MULTILINE, )
            lines = v.split("\n\n")
            lines = [s.replace(f"[{n}]", "███") if s[0] != '"' else s for s in lines]
            v = "\n\n".join(lines)
        else:
            v = v.replace(f"{s}: ", "")
    def make_link(m):
        g = m.group(1)
        if g in known_locations or g in known_characters:
            return g
        else:
            return f"[{g}]({g.replace(' ', '_')})"
    v = re.sub(r"\[(.*?)\]", make_link, v)
    v = v.replace("\n\n", "\n\n&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;")
    return v


def known_scenes_md():
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
    return " ".join(texts)


async def load(k):
    return await ft.SharedPreferences().get(k)


async def save(k, v):
    await ft.SharedPreferences().set(k, v)


md_style_sheet = ft.MarkdownStyleSheet(
    p_text_style=ft.TextStyle(size=18),
    text_alignment=ft.MainAxisAlignment.SPACE_EVENLY,
)


async def main(page: ft.Page):
    global current_scene, known_locations, known_scenes, known_characters
    page.title = "Late for Murder"
    page.fonts = {"Goudy": "fonts/GoudyBookletter1911-Regular.ttf"}
    page.theme = ft.Theme(font_family="Goudy")

    current_scene = await load("current_scene")
    current_scene = (
        tuple(current_scene) if current_scene else ("Scotland Yard", "22:35")
    )
    known_locations = await load("known_locations")
    known_locations = set(known_locations) if known_locations else {current_scene[0]}
    known_scenes = await load("known_scenes")
    known_scenes = (
        {tuple(ks.split("--")) for ks in known_scenes}
        if known_scenes
        else {current_scene}
    )
    await save("known_characters", [])
    known_characters = await load("known_characters")
    known_characters = set(known_characters) if known_characters else set()

    async def scene_tap_link(e):
        name = e.data.replace("_", " ")
        if name in characters.values():
            known_characters.add(name)
            await save("known_characters", sorted(known_characters))
        else:
            known_locations.add(name)
            await save("known_locations", sorted(known_locations))
            burrower_location.options = [
                ft.DropdownOption(kl) for kl in sorted(known_locations)
            ]
        await set_current_scene(*current_scene)

    def use_burrower_clicked(e):
        use_burrower_btn.visible = False
        use_burrower_controls.visible = True

    async def burrower_go_clicked(e):
        use_burrower_btn.visible = True
        use_burrower_controls.visible = False
        await set_current_scene(burrower_location.value, burrower_time.value)
        if current_scene in scenes:
            known_scenes.add(current_scene)
            await save(
                "known_scenes", sorted(f"{loc}--{time}" for (loc, time) in known_scenes)
            )
        timeline_md.value = known_scenes_md()

    async def timeline_click(e):
        loc, time = e.data.split("--")
        loc = loc.replace("_", " ")
        await set_current_scene(loc, time)

    async def set_current_scene(loc, time):
        global current_scene
        current_scene = loc, time
        await save("current_scene", list(current_scene))
        location_label.value = loc
        time_label.value = time
        scene_text_md.value = get_scene_md((loc, time))
        timeline_md.value = known_scenes_md()

    timeline_md = ft.Markdown(known_scenes_md(), on_tap_link=timeline_click)
    location_label = ft.Text(current_scene[0], size=25)
    time_label = ft.Text(current_scene[1], weight=ft.FontWeight.BOLD)
    scene_text_md = ft.Markdown(
        get_scene_md(current_scene),
        on_tap_link=scene_tap_link,
        md_style_sheet=md_style_sheet,
    )
    use_burrower_btn = ft.Button("Use Time Burrower", on_click=use_burrower_clicked)
    burrower_location = ft.Dropdown(
        label="Where", options=[ft.DropdownOption(kl) for kl in sorted(known_locations)]
    )
    burrower_time = ft.TextField(label="When")
    burrower_go_btn = ft.Button("Burrow!", on_click=burrower_go_clicked)
    use_burrower_controls = ft.Row(
        visible=False, controls=[burrower_location, burrower_time, burrower_go_btn]
    )

    page.scroll = ft.ScrollMode.AUTO
    page.add(
        ft.SafeArea(
            minimum_padding=20,
            content=ft.Column(
                controls=[
                    timeline_md,
                    ft.Divider(),
                    location_label,
                    time_label,
                    scene_text_md,
                    use_burrower_btn,
                    use_burrower_controls,
                ],
            ),
        )
    )


if __name__ == "__main__":
    ft.run(main)
