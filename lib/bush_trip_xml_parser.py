import math
import os
import shutil
import typing
import urllib
from dataclasses import dataclass
from xml.dom import minidom

from lib.flt_parser import FltParser
from lib.localization_strings import LocalizationStrings


def decdeg2dms(degs):
    neg = degs < 0
    degs = (-1) ** neg * degs
    degs, d_int = math.modf(degs)
    mins, m_int = math.modf(60 * degs)
    secs        =           60 * mins
    return math.trunc(d_int), math.trunc(m_int), math.trunc(secs)


@dataclass
class LegWaypoint:
    code: str
    name: str
    comment: str
    lat: float
    lon: float
    image_path: typing.Optional[str] = None
    new_image_path: typing.Optional[str] = None

    def skyvector_lat(self):
        c = 'N' if self.lat >= 0 else 'S'
        degrees, minutes, seconds = decdeg2dms(self.lat)
        return f"{degrees:02}{minutes:02}{seconds:02}{c}"

    def skyvector_lon(self):
        c = 'E' if self.lon >= 0 else 'W'
        degrees, minutes, seconds = decdeg2dms(self.lon)
        return f"{degrees:03}{minutes:02}{seconds:02}{c}"

@dataclass
class Leg:
    title: str
    waypoints: typing.List[LegWaypoint]

    def to_skyvector_plan_url(self, use_airport_code=False):
        first_waypoint = self.waypoints[0]
        last_waypoint = self.waypoints[-1]

        if use_airport_code:
            flight_plan = first_waypoint.code + " " + " ".join([f"{waypoint.skyvector_lat()}{waypoint.skyvector_lon()}" for waypoint in self.waypoints[1:-1]])  + " " + last_waypoint.code
        else:
            flight_plan = " ".join([f"{waypoint.skyvector_lat()}{waypoint.skyvector_lon()}" for waypoint in self.waypoints])
        return f"https://skyvector.com/?ll={first_waypoint.lat},{first_waypoint.lon}&chart=301&zoom=2&fpl={urllib.parse.quote(flight_plan)}"


class BushTripXMLParser:
    def __init__(self, file_path: str, localization_strings: LocalizationStrings, flt_parser: FltParser, image_prefix_path: str, pdf_image_path: str):
        desc = minidom.parse(file_path)


        self.legs: typing.List[Leg] = []

        # used for matching flight plan waypoints. has airports only once unlike legs which has airports on both departing and arriving leg
        self.waypoint_queue: typing.List[LegWaypoint] = []

        for i, legTag in enumerate(desc.getElementsByTagName('Leg')):
            leg_title_loc_id = legTag.getElementsByTagName("SimBase.Descr")[0].firstChild.nodeValue.split(":")[1]
            if localization_strings.is_translation_exists(leg_title_loc_id):
                title = localization_strings.translation_for(leg_title_loc_id)
            else: # sometimes leg titles are missing translation. Use just leg number.
                title = f"Leg {i+1}"

            leg = Leg(title, [])
            for sublegTag in legTag.getElementsByTagName('SubLeg'):
                poi = sublegTag.getElementsByTagName("ATCWaypointStart")[0].attributes['id'].value
                poi_desc = flt_parser.pop_next_name_for_poi(poi)
                comment = localization_strings.translation_for(sublegTag.getElementsByTagName("SimBase.Descr")[0].firstChild.nodeValue.split(":")[1])
                waypoint = LegWaypoint(poi, poi_desc.name, comment, poi_desc.lat, poi_desc.lon)
                leg.waypoints.append(waypoint)
                self.waypoint_queue.append(waypoint)

                image_tags = sublegTag.getElementsByTagName("ImagePath")
                if len(image_tags) > 0:
                    image_tag = image_tags[0].firstChild.nodeValue.strip()
                    if len(image_tag) > 0:
                        airport_poi = sublegTag.getElementsByTagName("ATCWaypointEnd")[0].attributes['id'].value
                        airport_info = flt_parser.get_next_name_for_poi(airport_poi)

                        image_path = os.path.join(image_prefix_path, image_tag)
                        if not os.path.exists(image_path):
                            # france has wrong image extension for legs?
                            image_path = image_path.replace("png", "jpg")

                        new_image_path = os.path.join(pdf_image_path, os.path.basename(image_path))

                        leg.waypoints.append(LegWaypoint(airport_poi, airport_info.name, "", airport_info.lat, airport_info.lon, image_path, new_image_path))

    def pop_waypoint(self):
        if len(self.waypoint_queue) == 0:
            return None

        return self.waypoint_queue.pop(0)

    def trip_to_html(self, html_path: str):
        output = ""
        for leg in self.legs:
            output += "<h2>" + leg.title + "</h2>"
            output += "<table>"
            for waypoint in leg.waypoints:
                output += "<tr><td style='white-space: nowrap'>"
                output += waypoint.code
                output += " (<a href='http://maps.google.com/maps/place/" + str(waypoint.lat) + "+" + str(waypoint.lon) + "' target='_blank'>Gmaps</a>,"
                output += " <a href='https://skyvector.com/?ll=" + str(waypoint.lat) + "," + str(waypoint.lon) + "&chart=301&zoom=2' target='_blank'>SkyVector</a>)"
                output += "</td><td>" + waypoint.name + "</td>"

                if waypoint.image_path is None:
                    output += "<td>" + waypoint.comment + "</td></tr>"
                else:
                    shutil.copy(waypoint.image_path, waypoint.new_image_path)
                    output += "<td><img src='file://" + waypoint.new_image_path + "'></td></tr>"

            output += "<tr><td colspan='3'>"
            output += "View as SkyVector Flight Plan (<a target='_blank' href='" + leg.to_skyvector_plan_url(True) + "'>with airport code</a>), (<a target='_blank' href='" + leg.to_skyvector_plan_url(False) + "'>without airport code</a>)</br>"
            output += "<p style='font: 8px, color: gray'>Note: Use without airport code version if the leg airports do not exist in the real world</p>"
            output += "</td></tr>"
            output += "</table>"

        output += "</body></html>"

        with open(html_path, 'w') as f:
            f.write(output)