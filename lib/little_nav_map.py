from lib.bush_trip_xml_parser import BushTripXMLParser
from yattag import Doc, indent

class LittleNavMap:
    def __init__(self, bush_trip_parser: BushTripXMLParser):
        self.bush_trip_parser = bush_trip_parser

    def generate_lnm_file(self, lnm_path):
        doc, tag, text = Doc().tagtext()

        doc.asis("""
            <?xml version="1.0" ?>
<LittleNavmap xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="https://www.littlenavmap.org/schema/lnmpln.xsd">
<Flightplan>  
    <Header>
      <FlightplanType>VFR</FlightplanType>
      <CruisingAlt>1000</CruisingAlt>
      <CreationDate>2022-02-24T18:12:22-08:00</CreationDate>
      <FileVersion>1.1</FileVersion>
      <ProgramName>Little Navmap</ProgramName>
      <ProgramVersion>2.6.17</ProgramVersion>
      <Documentation>https://www.littlenavmap.org/lnmpln.html</Documentation>
    </Header>
    <SimData>MSFS</SimData>
    <NavData Cycle="1801">NAVIGRAPH</NavData>
        """)
        with tag('Waypoints'):
            for i, leg in enumerate(self.bush_trip_parser.legs):
                for j, waypoint in enumerate(leg.waypoints):
                    if (j > 0 and waypoint.image_path) and i < len(self.bush_trip_parser.legs) - 1:
                        # do not add airport twice to the flight plan, unless this is the last leg
                        break
                    is_airport = True if j == 0 or j == (len(leg.waypoints) - 1) else False
                    with tag('Waypoint'):
                        with tag('Name'):
                            text(waypoint.name)
                        with tag('Ident'):
                            text(waypoint.code)
                        with tag('Type'):
                            text("AIRPORT" if is_airport else 'USER')
                        if not waypoint.image_path:
                            with tag('Pos', Lat=waypoint.lat, Lon=waypoint.lon, Alt="1000"):
                                pass
                        with tag("Comment"):
                            text(waypoint.comment)

        doc.asis("</Flightplan></LittleNavmap>")

        result = indent(
            doc.getvalue(),
            indentation = ' '*4,
            newline = '\r\n'
        )

        with open(lnm_path, "w", encoding="utf-8") as lnm:
            print("writing lnmpln to: ", lnm_path)
            lnm.write(result)
