import json
import re
from configparser import ConfigParser
from xml.dom import minidom

username = "Moshe Bergman"
bush_trip_folder = "asobo-bushtrip-nevada"
path_to_flt = r"Nevada.FLT"
path_to_xml = r"nevada.xml"
company = "Asobo"
bush_trip_path = r"C:\Users" + '\\' + username + r"\AppData\Roaming\Microsoft Flight Simulator\Packages\Official\Steam" + '\\' + bush_trip_folder + '\\'
inner_bush_trip_path = bush_trip_path + r"Missions" + '\\' + company + r"\BushTrips\nevada" + '\\'
lnmpln_path_original = r"C:\Users\Moshe Bergman\Documents\Flight Plans\Nevada\Main - VFR Breckenridge Airport (O64) to Mariposa-Yosemite (KMPI).lnmpln"
lnmpln_path_modified = r"C:\Users\Moshe Bergman\Documents\Flight Plans\Nevada\Main - VFR Breckenridge Airport (O64) to Mariposa-Yosemite (KMPI) - Modified.lnmpln"
html_path = r"C:\Users\Moshe Bergman\Documents\Flight Plans\Nevada\nevada.html"


with open(bush_trip_path + "en-US.locPak", "r") as file_contents:
    locPak = json.load(file_contents)
    strings = locPak['LocalisationPackage']['Strings']
    # ordered_strings = list(strings.keys())
    # ordered_strings.sort(key=lambda x: int(x.split('.')[2]))
    # for key in ordered_strings:
    #     #print(key, strings[key])
    #     pass

    poi_to_names = {}

    config = ConfigParser()
    config.read(inner_bush_trip_path + path_to_flt)
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


    desc = minidom.parse(inner_bush_trip_path + path_to_xml)

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

            image_tag = subleg.getElementsByTagName("ImagePath")[0].firstChild.nodeValue.strip()
            if len(image_tag) > 0:
                airport_poi = subleg.getElementsByTagName("ATCWaypointEnd")[0].attributes['id'].value
                airport_name = poi_to_names[airport_poi][0]
                output += "<tr><td>" + airport_poi + "</td><td>" + airport_name + "</td><td><img src='file://" + inner_bush_trip_path + image_tag + "' width='50%'></td></tr>"


        output += "</table>"

    output += "</body></html>"
    with open(html_path, 'w') as f:
        f.write(output)

    lnm_xml = minidom.parse(lnmpln_path_original)
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



    with open(lnmpln_path_modified, "w") as lnm:
        lnm.write(lnm_xml.toprettyxml(indent="  ", newl='\r'))