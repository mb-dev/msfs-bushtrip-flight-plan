import json
import re
from configparser import ConfigParser
from xml.dom import minidom



with open(r"C:\Users\Moshe Bergman\AppData\Roaming\Microsoft Flight Simulator\Packages\Official\Steam\asobo-bushtrip-nevada\en-US.locPak", "r") as file_contents:
    locPak = json.load(file_contents)
    strings = locPak['LocalisationPackage']['Strings']
    # ordered_strings = list(strings.keys())
    # ordered_strings.sort(key=lambda x: int(x.split('.')[2]))
    # for key in ordered_strings:
    #     #print(key, strings[key])
    #     pass

    poi_to_names = {}

    config = ConfigParser()
    config.read(r"C:\Users\Moshe Bergman\AppData\Roaming\Microsoft Flight Simulator\Packages\Official\Steam\asobo-bushtrip-nevada\Missions\Asobo\BushTrips\nevada\Nevada.FLT")
    for key, value in config.items('ATC_ActiveFlightPlan.0'):
        if key.startswith("waypoint"):
            parts = value.split(",")
            poi = parts[1].strip()

            if poi not in poi_to_names:
                poi_to_names[poi] = []

            if parts[3].strip().startswith("TT"):
                tt_key = parts[3].strip().split(":")[1]
                poi_to_names[poi].append(strings[tt_key])
            else:
                poi_to_names[poi].append(parts[3].strip())


    desc = minidom.parse(r'C:\Users\Moshe Bergman\AppData\Roaming\Microsoft Flight Simulator\Packages\Official\Steam\asobo-bushtrip-nevada\Missions\Asobo\BushTrips\nevada\Nevada.xml')

    sublegs = []

    output = """<html><head><link rel="stylesheet" href="https://unpkg.com/@picocss/pico@latest/css/pico.min.css"></head><body>"""
    for leg in desc.getElementsByTagName('Leg'):
        title = strings[leg.getElementsByTagName("SimBase.Descr")[0].firstChild.nodeValue.split(":")[1]]
        output += "<h2>" + title + "</h2>"
        output += "<table>"
        for subleg in leg.getElementsByTagName('SubLeg'):
            poi = subleg.getElementsByTagName("ATCWaypointStart")[0].attributes['id'].value
            poi_name = poi_to_names[poi].pop(0)
            comment = strings[subleg.getElementsByTagName("SimBase.Descr")[0].firstChild.nodeValue.split(":")[1]]
            sublegs.append({"name": poi_name, "comment": comment})
            output += "<tr><td>" + poi + "</td><td>" + poi_name + "</td><td>" + comment + "</td></tr>"
        output += "</table>"

    output += "</body></html>"
    with open(r"C:\Users\Moshe Bergman\Documents\Flight Plans\Nevada\nevada.html", 'w') as f:
        f.write(output)

    lnm_xml = minidom.parse(r"C:\Users\Moshe Bergman\Documents\Flight Plans\Nevada\Main - VFR Breckenridge Airport (O64) to Mariposa-Yosemite (KMPI).lnmpln")
    for waypoint in lnm_xml.getElementsByTagName('Waypoint'):
        if len(sublegs) == 0:
            break
        poi = sublegs.pop(0)

        comment_node = lnm_xml.createElement("Comment")
        comment_node.appendChild(lnm_xml.createTextNode(poi["comment"]))
        waypoint.appendChild(comment_node)

        if waypoint.getElementsByTagName("Type")[0].firstChild.nodeValue != "USER":
            continue

        name_node = lnm_xml.createElement("Name")
        name_node.appendChild(lnm_xml.createTextNode(poi["name"]))
        waypoint.appendChild(name_node)



    with open(r"C:\Users\Moshe Bergman\Documents\Flight Plans\Nevada\Main - VFR Breckenridge Airport (O64) to Mariposa-Yosemite (KMPI) - Modified.lnmpln", "w") as lnm:
        lnm_xml.writexml(lnm)