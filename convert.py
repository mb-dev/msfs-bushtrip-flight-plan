import asyncio
import shutil
import typing
from dataclasses import dataclass
import os
from xml.dom import minidom
import zipfile

from lib.bush_trip_xml_parser import BushTripXMLParser
from lib.flt_parser import FltParser
from lib.little_nav_map import LittleNavMap
from lib.localization_strings import LocalizationStrings
from lib.msfs_plan import MSFSPlan


@dataclass
class BushTripDesc:
    loc_pak_path: typing.Optional[str] = None
    flt_path: typing.Optional[str] = None
    spb_path: typing.Optional[str] = None
    xml_path: typing.Optional[str] = None
    image_prefix_path: typing.Optional[str] = None
    output_image_path: typing.Optional[str] = None
    lnmpln_path_original: typing.Optional[str] = None
    lnmpln_path_modified: typing.Optional[str] = None
    html_path: typing.Optional[str] = None
    pdf_path: typing.Optional[str] = None
    pdf_screenshot_path: typing.Optional[str] = None
    zip_path: typing.Optional[str] = None
    leg_plans_path: typing.Optional[str] = None




bush_trip_root_path =  r"C:\Users\Moshe Bergman\AppData\Roaming\Microsoft Flight Simulator\Packages\Official\Steam"
original_lnmpln_path = r"C:\Users\Moshe Bergman\Dropbox\Flight Plans\Original"
commented_lnmpln_path = r"C:\Users\Moshe Bergman\Dropbox\Flight Plans\Commented"
spb_to_xml_path = r"C:\MSFS\spb2xml-msfs-1.0.1\spb2xml-msfs.exe"
prop_def_path = r"C:\Program Files (x86)\Steam\steamapps\common\MicrosoftFlightSimulator\Packages\fs-base-propdefs\Propdefs\1.0\Common"

bush_trips = {
    "alaska": "asobo-bushtrip-alaska",
    "austria": "microsoft-bushtrip-austria",
    "balkans": "asobo-bushtrip-balkans",
    "chile": "asobo-bushtrip-chile",
    "denmark": "asobo-bushtrip-denmark",
    "finland": "asobo-bushtrip-finland",
    "france": "asobo-bushtrip-france",
    "germany": "microsoft-bushtrip-germany",
    "greatbarrier": "microsoft-bushtrip-greatbarrier",
    "grandalpine": "microsoft-bushtrip-grandalpine",
    "iceland": "asobo-bushtrip-iceland",
    "kimberley": "microsoft-bushtrip-kimberley",
    "nevada": r"asobo-bushtrip-nevada",
    "norway": "asobo-bushtrip-norway",
    "seadesert": "microsoft-bushtrip-seadesert",
    "seaus": "microsoft-bushtrip-seaus",
    "sweden": "asobo-bushtrip-sweden",
    "swiss": "microsoft-bushtrip-swiss",
    "tasmanian": "microsoft-bushtrip-tasmanian"
}

async def main():
    for trip_name, trip_sub_dir in bush_trips.items():

        # find all paths
        trip_desc = BushTripDesc(
            lnmpln_path_original=os.path.join(original_lnmpln_path, f"{trip_name}.lnmpln"),
            lnmpln_path_modified=os.path.join(commented_lnmpln_path, f"{trip_name}.lnmpln"),
            html_path=os.path.join(commented_lnmpln_path, f"{trip_name}.html"),
            pdf_path=os.path.join(commented_lnmpln_path, f"{trip_name}.pdf"),
            zip_path=os.path.join(commented_lnmpln_path, f"{trip_name}.zip"),
            output_image_path=os.path.join(commented_lnmpln_path, f"{trip_name}-files"),
            pdf_screenshot_path=os.path.join(commented_lnmpln_path, f"{trip_name}1.png"),
            leg_plans_path=os.path.join(commented_lnmpln_path, f"{trip_name}-leg-plans")
        )
        for path, subdirs, files in os.walk(os.path.join(bush_trip_root_path, trip_sub_dir)):
            for name in files:
                if name == "en-US.locPak":
                    trip_desc.loc_pak_path = os.path.join(path, name)
                elif ".flt" in name.lower():
                    trip_desc.flt_path = os.path.join(path, name)
                elif ".spb" in name.lower():
                    trip_desc.spb_path = os.path.join(path, name)
                    trip_desc.xml_path = os.path.join(path, name.replace(".spb", ".xml"))
                elif ".jpg" in name or ".png" in name:
                    trip_desc.image_prefix_path = os.path.abspath(os.path.join(path, ".."))

        os.makedirs(trip_desc.output_image_path, exist_ok=True)
        os.makedirs(trip_desc.leg_plans_path, exist_ok=True)

        # convert spb to xml
        if not os.path.exists(trip_desc.xml_path):
            spb_path = trip_desc.xml_path.replace(".xml", ".spb")
            convert_cmd = f"{spb_to_xml_path} -s \"{prop_def_path}\" \"{spb_path}\""
            print(convert_cmd)
            os.system(convert_cmd)

        # processing to pdf
        localization_strings = LocalizationStrings(trip_desc.loc_pak_path)
        flt_parser = FltParser(trip_desc.flt_path, localization_strings)
        bush_trip_xml_parser = BushTripXMLParser(trip_desc.xml_path, localization_strings, flt_parser, trip_desc.image_prefix_path, trip_desc.output_image_path)
        await bush_trip_xml_parser.trip_to_html(trip_desc.html_path, trip_desc.pdf_path, trip_desc.pdf_screenshot_path)

        # create little nav map plan
        little_nav_map = LittleNavMap(bush_trip_xml_parser)
        little_nav_map.generate_lnm_file(trip_desc.lnmpln_path_modified)

        # create leg plans
        msfs_plan = MSFSPlan(bush_trip_xml_parser)
        msfs_plan.create_leg_plans(trip_desc.leg_plans_path)

        # zip
        print(f"writing zip file {trip_desc.zip_path}")
        zipf = zipfile.ZipFile(trip_desc.zip_path, 'w', zipfile.ZIP_DEFLATED)
        zipf.write(trip_desc.pdf_path, os.path.basename(trip_desc.pdf_path))
        zipf.write(trip_desc.lnmpln_path_modified, os.path.basename(trip_desc.lnmpln_path_modified))
        zipf.write(trip_desc.leg_plans_path, os.path.basename(trip_desc.leg_plans_path))
        for leg_plan in msfs_plan.plan_files:
            zipf.write(leg_plan, os.path.join(os.path.basename(trip_desc.leg_plans_path), os.path.basename(leg_plan)))
        zipf.close()

asyncio.run(main())