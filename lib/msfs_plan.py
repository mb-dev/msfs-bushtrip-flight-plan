import os
import typing

from lib.bush_trip_xml_parser import BushTripXMLParser
from yattag import Doc, indent

class MSFSPlan:
    def __init__(self, bush_trip_parser: BushTripXMLParser):
        self.bush_trip_parser = bush_trip_parser
        self.plan_files: typing.List[str] = []

    def create_leg_plans(self, leg_plans_path: str):

        print("writing flight plans to: ", leg_plans_path)
        for i, leg in enumerate(self.bush_trip_parser.legs):
            doc, tag, text = Doc().tagtext()

            origin = leg.waypoints[0]
            dest = leg.waypoints[-1]

            doc.asis(f"""
<?xml version="1.0" encoding="UTF-8"?>
<SimBase.Document Type="AceXML" version="1,0">
    <Descr>AceXML Document</Descr>
    <FlightPlan.FlightPlan>
        <Title>{origin.code} - {dest.code}</Title>
        <FPType>VFR</FPType>
        <RouteType>Direct</RouteType>
        <CruisingAlt>1000</CruisingAlt>
        <DepartureID>{origin.code}</DepartureID>
        <DepartureLLA>{origin.orig_lat},{origin.orig_lon},+000000.00</DepartureLLA>
        <DestinationID>{dest.code}</DestinationID>
        <DestinationLLA>{dest.orig_lat},{dest.orig_lon},+000000.00</DestinationLLA>
        <Descr>{origin.code} - {dest.code}</Descr>
        <DepartureName>{origin.name}</DepartureName>
        <DestinationName>{dest.name}</DestinationName>
        <AppVersion>
            <AppVersionMajor>11</AppVersionMajor>
            <AppVersionBuild>282174</AppVersionBuild>
        </AppVersion>
            """)
            for j, waypoint in enumerate(leg.waypoints):
                with tag('ATCWaypoint', id=waypoint.code):
                    with tag('ATCWaypointType'):
                        text("Airport" if waypoint.is_airport else 'User')
                    with tag('WorldPosition'):
                        text(f"{waypoint.orig_lat},{waypoint.orig_lon},+000000.00")
                    if waypoint.image_path or j == 0:
                        with tag('ICAO'):
                            with tag('ICAOIdent'):
                                text(waypoint.code)

            doc.asis("</FlightPlan.FlightPlan></SimBase.Document>")

            result = indent(
                doc.getvalue(),
                indentation = ' '*4,
            )

            leg_plan_path = os.path.join(leg_plans_path, f"{i+1} - {origin.name} ({origin.code}) - {dest.name} ({dest.code}).pln")
            with open(leg_plan_path, "w", encoding="utf-8") as pln:
                pln.write(result)
            self.plan_files.append(leg_plan_path)
