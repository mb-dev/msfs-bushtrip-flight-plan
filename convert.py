import typing
import math
import urllib.parse
from dataclasses import dataclass
import os
import json
from dms2dec.dms_convert import dms2dec
from configparser import ConfigParser
from xml.dom import minidom

# to use for sky vector. returns truncated dms
def decdeg2dms(dd):
    dd = abs(dd)
    minutes,seconds = divmod(dd*3600,60)
    degrees,minutes = divmod(minutes,60)
    return (math.trunc(degrees),math.trunc(minutes),math.trunc(seconds))

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

@dataclass
class LegWaypoint:
    code: str
    name: str
    comment: str
    lat: float
    lon: float

    def skyvector_lat(self):
        c = 'N' if self.lat >= 0 else 'S'
        degrees, minutes, seconds = decdeg2dms(self.lat)
        return f"{degrees}{minutes}{seconds}{c}"

    def skyvector_lon(self):
        c = 'E' if self.lon >= 0 else 'W'
        degrees, minutes, seconds = decdeg2dms(self.lon)
        return f"{degrees}{minutes}{seconds}{c}"

@dataclass
class Leg:
    title: str
    waypoints: typing.List[LegWaypoint]

    def to_skyvector_plan_url(self):
        first_waypoint = self.waypoints[0]
        last_waypoint = self.waypoints[-1]

        flight_plan = first_waypoint.code + " " + " ".join([f"{waypoint.skyvector_lat()}{waypoint.skyvector_lon()}" for waypoint in self.waypoints[1:-1]])  + " " + last_waypoint.code
        return f"https://skyvector.com/?ll={first_waypoint.lat},{first_waypoint.lon}&chart=301&zoom=2&fpl={urllib.parse.quote(flight_plan)}"

bush_trip_root_path =  r"C:\Users\Moshe Bergman\AppData\Roaming\Microsoft Flight Simulator\Packages\Official\Steam"
original_lnmpln_path = r"C:\Users\Moshe Bergman\Dropbox\Flight Plans\Original"
commented_lnmpln_path = r"C:\Users\Moshe Bergman\Dropbox\Flight Plans\Commented"

bush_trips = {
    "alaska": BushTripDesc(
        loc_pak_path=os.path.join(bush_trip_root_path, r"asobo-bushtrip-alaska", "en-US.locPak"),
        flt_path=os.path.join(bush_trip_root_path, r"asobo-bushtrip-alaska\Missions\Asobo\BushTrips\Alaska", "Alaska.FLT"),
        xml_path=os.path.join(bush_trip_root_path, r"asobo-bushtrip-alaska\Missions\Asobo\BushTrips\Alaska", "alaska.xml"),
        image_prefix_path=os.path.join(bush_trip_root_path, r"asobo-bushtrip-alaska\Missions\Asobo\BushTrips\Alaska"),
        lnmpln_path_original=os.path.join(original_lnmpln_path, r"VFR Unalaska (PADU) to Kulik Lake (PAKL).lnmpln"),
        lnmpln_path_modified=os.path.join(commented_lnmpln_path, r"VFR Unalaska (PADU) to Kulik Lake (PAKL).lnmpln"),
        html_path=os.path.join(commented_lnmpln_path, r"alaska.html")
    ),
    "france": BushTripDesc(
        loc_pak_path=os.path.join(bush_trip_root_path, r"asobo-bushtrip-france", "en-US.locPak"),
        flt_path=os.path.join(bush_trip_root_path, r"asobo-bushtrip-france\Missions\Asobo\BushTrips\France", "france.FLT"),
        xml_path=os.path.join(bush_trip_root_path, r"asobo-bushtrip-france\Missions\Asobo\BushTrips\France", "france.xml"),
        image_prefix_path=os.path.join(bush_trip_root_path, r"asobo-bushtrip-france\Missions\Asobo\BushTrips\France"),
        lnmpln_path_original=os.path.join(original_lnmpln_path, r"VFR Leognan-Saucats (LFCS) to Megeve Airport (LFHM).lnmpln"),
        lnmpln_path_modified=os.path.join(commented_lnmpln_path, r"VFR Leognan-Saucats (LFCS) to Megeve Airport (LFHM).lnmpln"),
        html_path=os.path.join(commented_lnmpln_path, r"france.html")
    ),
    "grand-alpine": BushTripDesc(
        loc_pak_path=os.path.join(bush_trip_root_path, r"microsoft-bushtrip-grandalpine", "en-US.locPak"),
        flt_path=os.path.join(bush_trip_root_path, r"microsoft-bushtrip-grandalpine\Missions\Microsoft\BushTrips\grandalpinechallenge", "microsoft-bushtrip-grandalpinechallenge.FLT"),
        xml_path=os.path.join(bush_trip_root_path, r"microsoft-bushtrip-grandalpine\Missions\Microsoft\BushTrips\grandalpinechallenge", "microsoft-bushtrip-grandalpinechallenge.xml"),
        image_prefix_path=os.path.join(bush_trip_root_path, r"microsoft-bushtrip-grandalpine\Missions\Microsoft\BushTrips\grandalpinechallenge"),
        lnmpln_path_original=os.path.join(original_lnmpln_path, r"VFR La Cote (LSGP) to Aigen Im Ennstal (LOXA).lnmpln"),
        lnmpln_path_modified=os.path.join(commented_lnmpln_path, r"VFR La Cote (LSGP) to Aigen Im Ennstal (LOXA).lnmpln"),
        html_path=os.path.join(commented_lnmpln_path, r"grandalpinechallenge.html")
    ),
    "nevada": BushTripDesc(
        loc_pak_path=os.path.join(bush_trip_root_path, r"asobo-bushtrip-nevada", "en-US.locPak"),
        flt_path=os.path.join(bush_trip_root_path, r"asobo-bushtrip-nevada\Missions\Asobo\BushTrips\nevada", "Nevada.FLT"),
        xml_path=os.path.join(bush_trip_root_path, r"asobo-bushtrip-nevada\Missions\Asobo\BushTrips\nevada", "nevada.xml"),
        image_prefix_path=os.path.join(bush_trip_root_path, r"asobo-bushtrip-nevada\Missions\Asobo\BushTrips\nevada"),
        lnmpln_path_original=os.path.join(original_lnmpln_path, r"VFR Breckenridge Airport (O64) to Mariposa-Yosemite (KMPI).lnmpln"),
        lnmpln_path_modified=os.path.join(commented_lnmpln_path, r"VFR Breckenridge Airport (O64) to Mariposa-Yosemite (KMPI).lnmpln"),
        html_path=os.path.join(commented_lnmpln_path, r"nevada.html")
    ),
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
        legs = []

        output = """<html><head><link rel="stylesheet" href="https://unpkg.com/@picocss/pico@latest/css/pico.min.css"></head><body>"""
        for i, legTag in enumerate(desc.getElementsByTagName('Leg')):
            leg_title_loc_id = legTag.getElementsByTagName("SimBase.Descr")[0].firstChild.nodeValue.split(":")[1]
            if leg_title_loc_id in strings:
                title = strings[leg_title_loc_id]
            else: # sometimes leg titles are missing translation. Use just leg number.
                title = f"Leg {i+1}"

            leg = Leg(title, [])

            output += "<h2>" + leg.title + "</h2>"
            output += "<table>"
            for sublegTag in legTag.getElementsByTagName('SubLeg'):
                poi = sublegTag.getElementsByTagName("ATCWaypointStart")[0].attributes['id'].value
                poi_desc = poi_to_names[poi].pop(0)
                comment = strings[sublegTag.getElementsByTagName("SimBase.Descr")[0].firstChild.nodeValue.split(":")[1]]
                sublegs.append({"name": poi_desc.name, "comment": comment})
                leg.waypoints.append(LegWaypoint(poi, poi_desc.name, comment, poi_desc.lat, poi_desc.lon))
                output += "<tr><td style='white-space: nowrap'>"
                output += poi
                output += " (<a href='http://maps.google.com/maps/place/" + str(poi_desc.lat) + "+" + str(poi_desc.lon) + "' target='_blank'>Gmaps</a>,"
                output += " <a href='https://skyvector.com/?ll=" + str(poi_desc.lat) + "," + str(poi_desc.lon) + "&chart=301&zoom=2' target='_blank'>SkyVector</a>)"
                output += "</td><td>" + poi_desc.name + "</td><td>" + comment + "</td></tr>"

                image_tags = sublegTag.getElementsByTagName("ImagePath")
                if len(image_tags) > 0:
                    image_tag = image_tags[0].firstChild.nodeValue.strip()
                    if len(image_tag) > 0:
                        airport_poi = sublegTag.getElementsByTagName("ATCWaypointEnd")[0].attributes['id'].value
                        airport_info = poi_to_names[airport_poi][0]

                        leg.waypoints.append(LegWaypoint(airport_poi, airport_info.name, "", airport_info.lat, airport_info.lon))

                        image_path = os.path.join(trip_desc.image_prefix_path, image_tag)
                        if not os.path.exists(image_path):
                            # france has wrong image extension for legs?
                            image_path = image_path.replace("png", "jpg")

                        output += "<tr><td>" + airport_poi
                        output += " (<a href='http://maps.google.com/maps/place/" + str(airport_info.lat) + "+" + str(airport_info.lon) + "' target='_blank'>Gmaps</a>,"
                        output += " <a href='https://skyvector.com/?ll=" + str(airport_info.lat) + "," + str(airport_info.lon) + "&chart=301&zoom=2' target='_blank'>SkyVector</a>)"
                        output += "</td><td>" + airport_info.name + "</td><td><img src='file://" + image_path + "'></td></tr>"

            output += "<tr><td colspan='3'>"
            output += "<a target='_blank' href='" + leg.to_skyvector_plan_url() + "'>View as SkyVector Flight Plan</a></br>"
            output += "<p style='font: 8px, color: gray'>Note: Some flight simulator airports don\'t exist in the real world and either will not show up or appear in the wrong place in SkyVector</p>"
            output += "</td></tr>"
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