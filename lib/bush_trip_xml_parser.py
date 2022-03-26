import math
import os
import typing
import urllib
import urllib.request
from dataclasses import dataclass
from xml.dom import minidom
from PIL import Image
from pyppeteer import launch
import latlon
import spacy
from magnetic_field_calculator import MagneticFieldCalculator
from cachier import cachier
import datetime as dt

from lib.flt_parser import FltParser
from lib.localization_strings import LocalizationStrings
import humanize


def decdeg2dms(degs):
    neg = degs < 0
    degs = (-1) ** neg * degs
    degs, d_int = math.modf(degs)
    mins, m_int = math.modf(60 * degs)
    secs        =           60 * mins
    return math.trunc(d_int), math.trunc(m_int), math.trunc(secs)

# since this takes time, cache results locally
@cachier()
def get_waypoint_mag_declination(lat, lon):
    mag_field_calculator = MagneticFieldCalculator()
    result = mag_field_calculator.calculate(
        latitude=lat,
        longitude=lon,
        date='2028-12-31'
    )
    field_value = result['field-value']
    return field_value['declination']['value']

@dataclass
class LegWaypoint:
    code: str
    name: str
    comment: str
    lat: float
    orig_lat: str
    lon: float
    orig_lon: str
    image_path: typing.Optional[str] = None
    new_image_path: typing.Optional[str] = None
    distance: float = None
    heading: float = None
    minutes: float = 0

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
    total_nm: float = 0
    minutes: float = 0

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

        self.title = localization_strings.translation_for(flt_parser.title_tt)
        self.description = localization_strings.translation_for(flt_parser.description_tt)
        self.briefing = localization_strings.translation_for(flt_parser.briefing_tt)
        self.total_nm = 0
        self.minutes = 0

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
            self.legs.append(leg)

            sublegTags = legTag.getElementsByTagName('SubLeg')
            for i, sublegTag in enumerate(sublegTags):
                poi = sublegTag.getElementsByTagName("ATCWaypointStart")[0].attributes['id'].value

                # image handling
                image_tags = sublegTag.getElementsByTagName("ImagePath")
                image_path = None
                if len(image_tags) > 0:
                    image_tag = image_tags[0].firstChild.nodeValue.strip()
                    image_path = os.path.join(image_prefix_path, image_tag)
                    if not os.path.exists(image_path):
                        # france has wrong image extension for legs?
                        image_path = image_path.replace("png", "jpg")
                        if not os.path.exists(image_path):
                            # fix for seadesert
                            image_path = os.path.splitext(image_path)[0] + "__BRIEF" + ".jpg"

                    new_image_path = os.path.join(pdf_image_path, os.path.basename(image_path))

                poi_desc = flt_parser.pop_next_name_for_poi(poi)
                comment = localization_strings.translation_for(sublegTag.getElementsByTagName("SimBase.Descr")[0].firstChild.nodeValue.split(":")[1])

                waypoint = LegWaypoint(poi, poi_desc.name, comment, poi_desc.lat, poi_desc.orig_lat, poi_desc.lon, poi_desc.orig_lon)
                leg.waypoints.append(waypoint)
                self.waypoint_queue.append(waypoint)

                # put last leg image with the waypoint
                if i == len(sublegTags) - 1 and image_path:
                    airport_poi = sublegTag.getElementsByTagName("ATCWaypointEnd")[0].attributes['id'].value
                    airport_info = flt_parser.get_next_name_for_poi(airport_poi)
                    leg.waypoints.append(LegWaypoint(airport_poi, airport_info.name, "", airport_info.lat, airport_info.orig_lat, airport_info.lon, airport_info.orig_lon, image_path, new_image_path))
                elif image_path:
                    waypoint.image_path = image_path
                    waypoint.new_image_path = new_image_path

        for leg in self.legs:

            for i, waypoint in enumerate(leg.waypoints):
                if i+1 == len(leg.waypoints):
                    break

                from_waypoint = latlon.LatLon(waypoint.lat, waypoint.lon)
                to_waypoint = latlon.LatLon(leg.waypoints[i+1].lat, leg.waypoints[i+1].lon)
                waypoint.heading = from_waypoint.heading_initial(to_waypoint)
                if waypoint.heading < 0:
                    waypoint.heading = waypoint.heading + 360
                waypoint.heading = waypoint.heading - get_waypoint_mag_declination(waypoint.lat, waypoint.lon)
                waypoint.distance = from_waypoint.distance(to_waypoint, ellipse = 'sphere') * 0.5399568 # to nautical mile
                waypoint.minutes = waypoint.distance / (150 / 60.0) # assuming 150kts
                leg.total_nm += waypoint.distance
                leg.minutes += waypoint.minutes

            self.total_nm += leg.total_nm
            self.minutes += leg.minutes

    def pop_waypoint(self):
        if len(self.waypoint_queue) == 0:
            return None

        return self.waypoint_queue.pop(0)

    async def trip_to_html(self, html_path: str, pdf_path, screenshot_path):
        nlp = spacy.load("en_core_web_sm")

        print("writing html to: ", html_path)
        output = """<html><head><style>@page {
    margin-top: 0.75in;
    margin-bottom: 0.75in;
    margin-left: 0.75in;
    margin-right: 0.75in;    
}</style><link rel="stylesheet" href="https://unpkg.com/@picocss/pico@latest/css/pico.min.css"></head><body>"""
        output += "<h1>" + self.title + "</h1>"
        output += "<p>" + self.description + "</p>"
        output += "<p>" + self.briefing[:self.briefing.index("Assistance")] + "</p>"
        output += f"<p>Total distance: {self.total_nm:.0f}nm, Total ETE with 150kts aircraft: {humanize.precisedelta(dt.timedelta(minutes=self.minutes), minimum_unit='minutes', format='%.0f')}</p>"
        for leg in self.legs:
            output += "<h2>" + leg.title + "</h2>"
            output += "<table>"
            for i, waypoint in enumerate(leg.waypoints):
                output += "<tr><td style='white-space: nowrap'>"
                output += waypoint.code
                output += "<br/> (<a href='http://maps.google.com/maps/place/" + str(waypoint.lat) + "+" + str(waypoint.lon) + "' target='_blank'>Gmaps</a>,"
                output += " <a href='https://skyvector.com/?ll=" + str(waypoint.lat) + "," + str(waypoint.lon) + "&chart=301&zoom=2' target='_blank'>SkyVector</a>)"
                if waypoint.heading and waypoint.distance:
                    output += f"<br/>{waypoint.heading:.0f}&deg; {waypoint.distance:.1f}nm {waypoint.minutes:.1f} minutes"
                output += f"</td><td>{waypoint.name}"
                output += "</td>"

                comment = waypoint.comment
                if comment:
                    doc = nlp(comment)
                    for ent in doc.ents:
                        if ent.label_ == "LOC" or ent.label_ == "ORG" or ent.label_ == "PERSON" or ent.label_ == "GPE":
                            comment = comment.replace(ent.text, "<a target='_blank' href='https://www.google.com/search?q=" + ent.text + "'>" + ent.text + "</a>")

                if waypoint.image_path is None:
                    output += "<td>" + comment + "</td></tr>"
                else:
                    # resize image
                    if not os.path.exists(waypoint.new_image_path):
                        print("resizing image", waypoint.image_path)
                        basewidth = 900
                        img = Image.open(waypoint.image_path)
                        wpercent = (basewidth/float(img.size[0]))
                        hsize = int((float(img.size[1])*float(wpercent)))
                        img = img.resize((basewidth, hsize), Image.ANTIALIAS)
                        # save resized image
                        img.save(waypoint.new_image_path)
                    output += "<td><img src='" + urllib.request.pathname2url(waypoint.new_image_path) + f"'>"

                    if comment:
                        output += f"<p>{comment}</p>"

                    output += "</td></tr>"

            output += "<tr><td colspan='3'>"
            output += "View as SkyVector Flight Plan (<a target='_blank' href='" + leg.to_skyvector_plan_url(True) + "'>with airport code</a>), (<a target='_blank' href='" + leg.to_skyvector_plan_url(False) + "'>without airport code</a>)</br>"
            output += "<p style='font: 8px, color: gray'>Note: Use without airport code version if the leg airports do not exist in the real world</p>"
            output += f"Total distance: {leg.total_nm:.0f}nm, ETE with 150kts aircraft: {humanize.precisedelta(dt.timedelta(minutes=leg.minutes), minimum_unit='minutes', format='%.0f')}"
            output += "</td></tr>"
            output += "</table>"

        output += "</body></html>"

        with open(html_path, 'w', encoding="utf-8") as f:
            f.write(output)

        print("generating pdf", pdf_path)
        regenerate = True
        if regenerate or not os.path.exists(pdf_path):
            browser = await launch({
                'executablePath': r"C:\Program Files\Google\Chrome\Application\chrome.exe"
            })
            page = await browser.newPage()
            await page.goto(html_path)
            await page.setViewport({ "width": 1600, "height": 1200 });
            await page.screenshot({"path": screenshot_path})
            await page.pdf({
                'path': pdf_path,
                'format': 'A4',
            })
            await browser.close()