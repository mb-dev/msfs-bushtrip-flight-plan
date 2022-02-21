from dataclasses import dataclass
import os
import json
import urllib.parse as urllib
import re
from dms2dec.dms_convert import dms2dec
from configparser import ConfigParser
from xml.dom import minidom

def fix_lat_lon(str):
    return str[1:] + str[0]

@dataclass
class BushTripDesc:
    loc_pak_path: str
    flt_path: str
    xml_path: str
    image_prefix_path: str
    lnmpln_path_original: str
    lnmpln_path_modified: str
    html_path: str

@dataclass
class POIDesc:
    name: str
    lat: float
    lon: float

bush_trip_root_path =  r"C:\Users\Moshe Bergman\AppData\Roaming\Microsoft Flight Simulator\Packages\Official\Steam"
original_lnmpln_path = r"C:\Users\Moshe Bergman\Dropbox\Flight Plans\Original"
commented_lnmpln_path = r"C:\Users\Moshe Bergman\Dropbox\Flight Plans\Commented"

bush_trips = {
    "nevada": BushTripDesc(
        loc_pak_path=os.path.join(bush_trip_root_path, r"asobo-bushtrip-nevada", "en-US.locPak"),
        flt_path=os.path.join(bush_trip_root_path, r"asobo-bushtrip-nevada\Missions\Asobo\BushTrips\nevada", "Nevada.FLT"),
        xml_path=os.path.join(bush_trip_root_path, r"asobo-bushtrip-nevada\Missions\Asobo\BushTrips\nevada", "nevada.xml"),
        image_prefix_path=os.path.join(bush_trip_root_path, r"asobo-bushtrip-nevada\Missions\Asobo\BushTrips\nevada"),
        lnmpln_path_original=os.path.join(original_lnmpln_path, r"VFR Breckenridge Airport (O64) to Mariposa-Yosemite (KMPI).lnmpln"),
        lnmpln_path_modified=os.path.join(commented_lnmpln_path, r"VFR Breckenridge Airport (O64) to Mariposa-Yosemite (KMPI).lnmpln"),
        html_path=os.path.join(commented_lnmpln_path, r"nevada.html")
    ),
    "france": BushTripDesc(
        loc_pak_path=os.path.join(bush_trip_root_path, r"asobo-bushtrip-france", "en-US.locPak"),
        flt_path=os.path.join(bush_trip_root_path, r"asobo-bushtrip-france\Missions\Asobo\BushTrips\France", "france.FLT"),
        xml_path=os.path.join(bush_trip_root_path, r"asobo-bushtrip-france\Missions\Asobo\BushTrips\France", "france.xml"),
        image_prefix_path=os.path.join(bush_trip_root_path, r"asobo-bushtrip-france\Missions\Asobo\BushTrips\France"),
        lnmpln_path_original=os.path.join(original_lnmpln_path, r"VFR Leognan-Saucats (LFCS) to Megeve Airport (LFHM).lnmpln"),
        lnmpln_path_modified=os.path.join(commented_lnmpln_path, r"VFR Leognan-Saucats (LFCS) to Megeve Airport (LFHM).lnmpln"),
        html_path=os.path.join(commented_lnmpln_path, r"france.html")
    )
}

for trip_name, trip_desc in bush_trips.items():
    with open(trip_desc.loc_pak_path, "r") as file_contents:
        locPak = json.load(file_contents)
        strings = locPak['LocalisationPackage']['Strings']

        poi_to_names = {}

        config = ConfigParser()
        config.read(trip_desc.flt_path)
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
                    poi_to_names[poi].append(POIDesc(strings[tt_key], lat, lon))
                else:
                    poi_to_names[poi].append(POIDesc(parts[3].strip(), lat, lon))


        desc = minidom.parse(trip_desc.xml_path)

        sublegs = []

        output = """<html><head><link rel="stylesheet" href="https://unpkg.com/@picocss/pico@latest/css/pico.min.css"></head><body>"""
        for i, leg in enumerate(desc.getElementsByTagName('Leg')):
            desc_loc_id = leg.getElementsByTagName("SimBase.Descr")[0].firstChild.nodeValue.split(":")[1]
            if desc_loc_id in strings:
                title = strings[desc_loc_id]
            else:
                title = f"Leg {i+1}"
            output += "<h2>" + title + "</h2>"
            output += "<table>"
            for subleg in leg.getElementsByTagName('SubLeg'):
                poi = subleg.getElementsByTagName("ATCWaypointStart")[0].attributes['id'].value
                poi_desc = poi_to_names[poi].pop(0)
                comment = strings[subleg.getElementsByTagName("SimBase.Descr")[0].firstChild.nodeValue.split(":")[1]]
                sublegs.append({"name": poi_desc.name, "comment": comment})
                output += "<tr><td style='white-space: nowrap'>"
                output += poi
                output += " (<a href='http://maps.google.com/maps/place/" + str(poi_desc.lat) + "+" + str(poi_desc.lon) + "' target='_blank'>Gmaps</a>,"
                output += " <a href='https://skyvector.com/?ll=" + str(poi_desc.lat) + "," + str(poi_desc.lon) + "&chart=301&zoom=2' target='_blank'>SkyVector</a>)"
                output += "</td><td>" + poi_desc.name + "</td><td>" + comment + "</td></tr>"

                image_tags = subleg.getElementsByTagName("ImagePath")
                if len(image_tags) > 0:
                    image_tag = image_tags[0].firstChild.nodeValue.strip()
                    if len(image_tag) > 0:
                        airport_poi = subleg.getElementsByTagName("ATCWaypointEnd")[0].attributes['id'].value
                        airport_info = poi_to_names[airport_poi][0]

                        image_path = os.path.join(trip_desc.image_prefix_path, image_tag)
                        if not os.path.exists(image_path):
                            # france has wrong image extension for legs?
                            image_path = image_path.replace("png", "jpg")

                        output += "<tr><td>" + airport_poi
                        output += " (<a href='http://maps.google.com/maps/place/" + str(airport_info.lat) + "+" + str(airport_info.lon) + "' target='_blank'>Gmaps</a>,"
                        output += " <a href='https://skyvector.com/?ll=" + str(airport_info.lat) + "," + str(airport_info.lon) + "&chart=301&zoom=2' target='_blank'>SkyVector</a>)"
                        output += "</td><td>" + airport_info.name + "</td><td><img src='file://" + image_path + "' width='50%'></td></tr>"


            output += "</table>"

        output += "</body></html>"
        with open(trip_desc.html_path, 'w') as f:
            f.write(output)

        lnm_xml = minidom.parse(trip_desc.lnmpln_path_original)
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



        with open(trip_desc.lnmpln_path_modified, "w") as lnm:
            lnm.write(lnm_xml.toprettyxml(indent="  "))