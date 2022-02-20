import json
import urllib.parse as urllib
import re
from dms2dec.dms_convert import dms2dec
from configparser import ConfigParser
from xml.dom import minidom

path_to_locPak = r"C:\Users\Moshe Bergman\AppData\Roaming\Microsoft Flight Simulator\Packages\Official\Steam\asobo-bushtrip-nevada\en-US.locPak"
path_to_flt = r"C:\Users\Moshe Bergman\AppData\Roaming\Microsoft Flight Simulator\Packages\Official\Steam\asobo-bushtrip-nevada\Missions\Asobo\BushTrips\nevada\Nevada.FLT"
path_to_xml = r"C:\Users\Moshe Bergman\AppData\Roaming\Microsoft Flight Simulator\Packages\Official\Steam\asobo-bushtrip-nevada\Missions\Asobo\BushTrips\nevada\nevada.xml"
image_path_prefix = r"C:\Users\Moshe Bergman\AppData\Roaming\Microsoft Flight Simulator\Packages\Official\Steam\asobo-bushtrip-nevada\Missions\Asobo\BushTrips\nevada" + '\\'
lnmpln_path_original = r"C:\Users\Moshe Bergman\Documents\Flight Plans\Nevada\Main - VFR Breckenridge Airport (O64) to Mariposa-Yosemite (KMPI).lnmpln"
lnmpln_path_modified = r"C:\Users\Moshe Bergman\Documents\Flight Plans\Nevada\Main - VFR Breckenridge Airport (O64) to Mariposa-Yosemite (KMPI) - Modified.lnmpln"
html_path = r"C:\Users\Moshe Bergman\Dropbox\Flight Plans\nevada.html"

def fix_lat_lon(str):
    return str[1:] + str[0]

with open(path_to_locPak, "r") as file_contents:
    locPak = json.load(file_contents)
    strings = locPak['LocalisationPackage']['Strings']
    # ordered_strings = list(strings.keys())
    # ordered_strings.sort(key=lambda x: int(x.split('.')[2]))
    # for key in ordered_strings:
    #     #print(key, strings[key])
    #     pass

    poi_to_names = {}

    config = ConfigParser()
    config.read(path_to_flt)
    for key, value in config.items('ATC_ActiveFlightPlan.0'):
        if key.startswith("waypoint"):
            parts = value.split(",")
            poi = parts[1].strip()
            lat = dms2dec(fix_lat_lon(parts[5].strip()))
            lon = dms2dec(fix_lat_lon(parts[6].strip()))

            if poi not in poi_to_names:
                poi_to_names[poi] = []

            if parts[3].strip().startswith("TT"):
                tt_key = parts[3].strip().split(":")[1]
                poi_to_names[poi].append({"str": strings[tt_key], "lat": lat, "lon": lon})
            else:
                poi_to_names[poi].append({"str": parts[3].strip(), "lat": lat, "lon": lon})


    desc = minidom.parse(path_to_xml)

    sublegs = []

    output = """<html><head><link rel="stylesheet" href="https://unpkg.com/@picocss/pico@latest/css/pico.min.css"></head><body>"""
    for leg in desc.getElementsByTagName('Leg'):
        title = strings[leg.getElementsByTagName("SimBase.Descr")[0].firstChild.nodeValue.split(":")[1]]
        output += "<h2>" + title + "</h2>"
        output += "<table>"
        for subleg in leg.getElementsByTagName('SubLeg'):
            poi = subleg.getElementsByTagName("ATCWaypointStart")[0].attributes['id'].value
            poi_info = poi_to_names[poi].pop(0)
            poi_name = poi_info["str"]
            poi_lat = poi_info["lat"]
            poi_lon = poi_info["lon"]
            comment = strings[subleg.getElementsByTagName("SimBase.Descr")[0].firstChild.nodeValue.split(":")[1]]
            sublegs.append({"name": poi_name, "comment": comment})
            output += "<tr><td style='white-space: nowrap'>"
            output += poi
            output += " (<a href='http://maps.google.com/maps/place/" + str(poi_lat) + "+" + str(poi_lon) + "' target='_blank'>Gmaps</a>,"
            output += " <a href='https://skyvector.com/?ll=" + str(poi_lat) + "," + str(poi_lon) + "&chart=301&zoom=2' target='_blank'>SkyVector</a>)"
            output += "</td><td>" + poi_name + "</td><td>" + comment + "</td></tr>"

            image_tag = subleg.getElementsByTagName("ImagePath")[0].firstChild.nodeValue.strip()
            if len(image_tag) > 0:
                airport_poi = subleg.getElementsByTagName("ATCWaypointEnd")[0].attributes['id'].value
                airport_info = poi_to_names[airport_poi][0]
                airport_name = airport_info["str"]
                airport_lat = airport_info["lat"]
                airport_lon = airport_info["lon"]
                output += "<tr><td>" + airport_poi
                output += " (<a href='http://maps.google.com/maps/place/" + str(airport_lat) + "+" + str(airport_lon) + "' target='_blank'>Gmaps</a>,"
                output += " <a href='https://skyvector.com/?ll=" + str(airport_lat) + "," + str(airport_lon) + "&chart=301&zoom=2' target='_blank'>SkyVector</a>)"
                output += "</td><td>" + airport_name + "</td><td><img src='file://" + image_path_prefix + image_tag + "' width='50%'></td></tr>"


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