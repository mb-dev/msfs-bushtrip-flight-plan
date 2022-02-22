import shutil
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
from lib.bush_trip_xml_parser import BushTripXMLParser
from lib.flt_parser import FltParser
from lib.localization_strings import LocalizationStrings




@dataclass
class BushTripDesc:
    loc_pak_path: str
    flt_path: str
    xml_path: str
    image_prefix_path: str
    lnmpln_path_original: str
    lnmpln_path_modified: str
    html_path: str




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
    pdf_image_path = os.path.join(commented_lnmpln_path, f"{trip_name}-files")
    os.makedirs(pdf_image_path, exist_ok=True)

    localization_strings = LocalizationStrings(trip_desc.loc_pak_path)
    flt_parser = FltParser(trip_desc.flt_path, localization_strings)
    bush_trip_xml_parser = BushTripXMLParser(trip_desc.xml_path, localization_strings, flt_parser, trip_desc.image_prefix_path, pdf_image_path)
    bush_trip_xml_parser.trip_to_html(trip_desc.html_path)

    # ----
    # 3. make pdf

    lnm_xml = minidom.parse(trip_desc.lnmpln_path_original)
    for waypoint in lnm_xml.getElementsByTagName('Waypoint'):
        bush_trip_xml_waypoint = bush_trip_xml_parser.pop_waypoint()
        if bush_trip_xml_waypoint is None:
            break

        comment_node = lnm_xml.createElement("Comment")
        comment_node.appendChild(lnm_xml.createTextNode(bush_trip_xml_waypoint.comment))
        waypoint.appendChild(comment_node)

        if waypoint.getElementsByTagName("Type")[0].firstChild.nodeValue != "USER":
            continue

        name_node = lnm_xml.createElement("Name")
        name_node.appendChild(lnm_xml.createTextNode(bush_trip_xml_waypoint.name))
        waypoint.appendChild(name_node)



    with open(trip_desc.lnmpln_path_modified, "w") as lnm:
        lnm.write(lnm_xml.toprettyxml(indent="  "))