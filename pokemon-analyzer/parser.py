import re
import os
import string


def parseTeams():
    team_dataset = []

    files_ary = []
    for filename in os.listdir("teams"):
        if filename.endswith(".txt"):
            files_ary.append(os.path.join("teams", filename))
            continue
        else:
            continue

    for file_path in files_ary:
        team_txt = open(file_path, "r")
        team = []
        if team_txt.mode == 'r':

            contents = team_txt.read().strip()

            # We will remove all non-ASCII characters so our parser plays nicely with it
            # (no non-ascii chars are needed in the data we are using)
            printable = set(string.printable)
            contents = filter(lambda x: x in printable,contents)

            # Cleans some data up that accidentally put too many spaces in between different Pokemon
            contents=contents.replace("\n\n\n","\n\n")

            team_split = contents.split("\n\n")

            if(len(team_split)) > 6:
                raise Exception('The size of a team should not exceed 6.')

            # We iterate through each pkmn listed in this file
            for pkmn_txt in team_split:

                line_number = 0

                pkmn = {} # We create a dictionary for this pokemon.

                pkmn_split = pkmn_txt.split("\n")

                # Before we parse EVs and IVs, we default their values to 0 (and 31 for IVs) for ones that are not parsed.
                for ev_type in ["HP", "Atk", "Def", "SpA", "SpD", "Spe"]:
                    pkmn["ev_"+ev_type] = 0
                    pkmn["iv_"+ev_type] = 31


                # The Pokemon may have a name. We check to see if it does, and if so, cull the name
                # "Johnny (Slowbro-Mega) @ Slowbronite"
                # "Johnny (Slowbro) (M) @ Slowbronite" if there is a gender - which we ignore
                match = re.match("([\w\-\s\'\!\?]+)(\([\w\-\s]{2,}\))\s*(\([MF]\))?\s*(@\s*([\w\-\s]+))?", pkmn_split[line_number].strip())
                if match is not None:
                        # there is a nickname, so we cull it
                        comp = re.compile("[\w\-\s\'\!\?]+\(")
                        pkmn_split[line_number] = comp.sub('',pkmn_split[line_number],1)
                        comp = re.compile("\)")
                        pkmn_split[line_number] = comp.sub('',pkmn_split[line_number],1)


                # If there is no nickname, Line 0 should be of form:
                # "Slowbro-Mega @ Slowbronite"
                # "Slowbro (M) @ Slowbronite" if there is a gender - which we ignore
                # species @ item
                match = re.match("([\w\-\s]+)(\([MF]\))?\s*(@\s*([\w\-\s]+))?", pkmn_split[line_number].strip())
                if match is None:
                    print("ERROR: The following Pokemon is not valid:")
                    print(pkmn_split[line_number].strip())
                    continue

                pkmn["Species"] = match.group(1).strip()
                pkmn["Item"] = (match.group(4) if match.group(4) is not None else "")
                line_number += 1

                # The next line is an OPTIONAL ability line:
                # "Ability: Regenerator"
                # "Ability: <item>
                match = re.match("Ability:\s*([\w\-]+)", pkmn_split[line_number].strip())
                if match is not None:
                    pkmn["Ability"] = match.group(1)
                    line_number += 1

                # The next line is an OPTIONAL EVs line:
                # "EVs: 252 HP / 252 Def / 4 SpD  "
                # "EVs: <number> HP / <number> Atk" etc... each field is optional.
                exists = re.match("EVs: (.*)",pkmn_split[line_number].strip())
                if exists is not None:
                    ev_string = exists.group(1)
                    ev_array = ev_string.split(" / ")
                    for ev in ev_array:
                        parseEVIV("ev", ev, pkmn)
                    line_number += 1

                # The next line is an OPTIONAL Nature line.
                # "Bold Nature"
                # "<nature> Nature"
                match = re.match("([\w\-]+) Nature", pkmn_split[line_number].strip())
                if match is not None:
                    pkmn["Nature"] = match.group(1)
                    line_number += 1
                else:
                    pkmn["Nature"] = "Serious"

                # Every subsequent line is necessarily a move.
                # "- Slack Off"
                # "- <move name"
                move_number = 0
                pkmn["Moves"] = []
                while line_number < len(pkmn_split):
                    match = re.match("-\s([\'\w\d\s\-\[\]]+)", pkmn_split[line_number].strip())
                    if match is not None:
                        pkmn["Moves"].append(match.group(1).replace("[", "").replace("]", "").strip())
                        move_number += 1
                    line_number += 1

                team.append(pkmn)
        team_dataset.append(team)

    # TODO: maybe we can store this and access it in the future?

    # TODO: do sepcial handling for megas. cull "MEGA" part from species, store, and set item

    return team_dataset


# Parses an individual EV/IV in the EV/IV setting line and appends it to the block of pokemon.
def parseEVIV(eviv, string,pkmn):
    # HP
    match = re.match("\s*(\d+) HP\s*", string)
    if match is not None:
        pkmn[eviv+"_HP"] = int(match.group(1))
    # Atk
    match = re.match("\s*(\d+) Atk\s*", string)
    if match is not None:
        pkmn[eviv+"_Atk"] = int(match.group(1))
    # Def
    match = re.match("\s*(\d+) Def\s*", string)
    if match is not None:
        pkmn[eviv+"_Def"] = int(match.group(1))
    # SpA
    match = re.match("\s*(\d+) SpA\s*", string)
    if match is not None:
        pkmn[eviv+"_SpA"] = int(match.group(1))
    # SpD
    match = re.match("\s*(\d+) SpD\s*", string)
    if match is not None:
        pkmn[eviv+"_SpD"] = int(match.group(1))
    # Spe
    match = re.match("\s*(\d+) Spe\s*", string)
    if match is not None:
        pkmn[eviv+"_Spe"] = int(match.group(1))


if __name__ == "__main__":
    parseTeams()