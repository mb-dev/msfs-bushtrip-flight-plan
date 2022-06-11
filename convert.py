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
    lnmpln_path: typing.Optional[str] = None
    html_path: typing.Optional[str] = None
    pdf_path: typing.Optional[str] = None
    pdf_screenshot_path: typing.Optional[str] = None
    leg_plans_path: typing.Optional[str] = None




official_bush_trip_root_path =  r"C:\Users\Moshe Bergman\AppData\Roaming\Microsoft Flight Simulator\Packages\Official\Steam"
community_bush_trip_path = r"C:\MSFS\MSFS_Addons_Linker_v13e_1I0B2\Linker_Community\Bush Trips"
output_base_path = r"C:\Users\Moshe Bergman\Dropbox\Flight Plans\Commented"
spb_to_xml_path = r"C:\MSFS\spb2xml-msfs-1.0.1\spb2xml-msfs.exe"
prop_def_path = r"C:\Program Files (x86)\Steam\steamapps\common\MicrosoftFlightSimulator\Packages\fs-base-propdefs\Propdefs\1.0\Common"

bush_trips = {
    "aio": {
        "apennines": os.path.join(official_bush_trip_root_path, "microsoft-bushtrip-apennines"),
        "alaska": os.path.join(official_bush_trip_root_path, "asobo-bushtrip-alaska"),
        "austria": os.path.join(official_bush_trip_root_path, "microsoft-bushtrip-austria"),
        "balkans": os.path.join(official_bush_trip_root_path, "asobo-bushtrip-balkans"),
        "chile": os.path.join(official_bush_trip_root_path, "asobo-bushtrip-chile"),
        "denmark": os.path.join(official_bush_trip_root_path, "asobo-bushtrip-denmark"),
        "finland": os.path.join(official_bush_trip_root_path, "asobo-bushtrip-finland"),
        "france": os.path.join(official_bush_trip_root_path, "asobo-bushtrip-france"),
        "germany": os.path.join(official_bush_trip_root_path, "microsoft-bushtrip-germany"),
        "greatbarrier": os.path.join(official_bush_trip_root_path, "microsoft-bushtrip-greatbarrier"),
        "grandalpine": os.path.join(official_bush_trip_root_path, "microsoft-bushtrip-grandalpine"),
        "iberiaconnection": os.path.join(official_bush_trip_root_path, "microsoft-bushtrip-iberiaconnection"),
        "iceland": os.path.join(official_bush_trip_root_path, "asobo-bushtrip-iceland"),
        "kimberley": os.path.join(official_bush_trip_root_path, "microsoft-bushtrip-kimberley"),
        "medcoast": os.path.join(official_bush_trip_root_path, "microsoft-bushtrip-medcoast"),
        "nevada": os.path.join(official_bush_trip_root_path, r"asobo-bushtrip-nevada"),
        "norway": os.path.join(official_bush_trip_root_path, "asobo-bushtrip-norway"),
        "portugal": os.path.join(official_bush_trip_root_path, "microsoft-bushtrip-portugal"),
        "pyrenees": os.path.join(official_bush_trip_root_path, "microsoft-bushtrip-pyrenees"),
        "sardinia": os.path.join(official_bush_trip_root_path, "microsoft-bushtrip-sardinia"),
        "sicily": os.path.join(official_bush_trip_root_path, "microsoft-bushtrip-sicily"),
        "seadesert": os.path.join(official_bush_trip_root_path, "microsoft-bushtrip-seadesert"),
        "seaus": os.path.join(official_bush_trip_root_path, "microsoft-bushtrip-seaus"),
        "sweden": os.path.join(official_bush_trip_root_path, "asobo-bushtrip-sweden"),
        "swiss": os.path.join(official_bush_trip_root_path, "microsoft-bushtrip-swiss"),
        "tasmanian": os.path.join(official_bush_trip_root_path, "microsoft-bushtrip-tasmanian"),
    }
    # "i-a-t": [{
    #     "name": "i-a-t-13-part1-DA62",
    #     "path": os.path.join(community_bush_trip_path, "i-a-t-13-part1-DA62"),
    # }, {
    #     "name": "i-a-t-13-part2-DA62",
    #     "path": os.path.join(community_bush_trip_path, "i-a-t-13-part2-DA62"),
    # }, {
    #     "name": "i-a-t-13-part3-DA62",
    #     "path": os.path.join(community_bush_trip_path, "i-a-t-13-part3-DA62"),
    # }, {
    #     "name": "i-a-t-13-part4-DA62",
    #     "path": os.path.join(community_bush_trip_path, "i-a-t-13-part4-DA62"),
    # }],
    # "germany-tour": [{
    #     "name": "germany-tour-part1",
    #     "path": os.path.join(community_bush_trip_path, r"Germany\Deutschland-Tour-Teil1"),
    # }],
    # "discover-spain": [{
    #     "name": "discover-spain-part1",
    #     "path": os.path.join(community_bush_trip_path, r"Spain\IFRSanSebastian-SanSebastian-Mission"),
    # }],
    # "mission-pakn-pamk": os.path.join(community_bush_trip_path, "Alaska\mission-pakn-pamk"),
    # "sbt-p1-mission": os.path.join(community_bush_trip_path, "SBT-p1-Mission"),
}

async def main():
    for package_name, bush_trip_path_arr in bush_trips.items():

        # ensure path is array
        if not isinstance(bush_trip_path_arr, list):
            if isinstance(bush_trip_path_arr, str):
                # old style
                bush_trip_path_arr = [{"name": package_name, "path": bush_trip_path_arr}]
            else:
                # aio style
                bush_trip_path_arr = [{"name": name, "path": path} for name, path in bush_trip_path_arr.items()]


        # prepare zip
        zip_path = os.path.join(output_base_path, f"{package_name}.zip")
        zipf = zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED)

        for part in bush_trip_path_arr:
            trip_name = part["name"]
            bush_trip_path = part["path"]

            # find all paths
            trip_desc = BushTripDesc(
                lnmpln_path=os.path.join(output_base_path, f"{trip_name}.lnmpln"),
                html_path=os.path.join(output_base_path, f"{trip_name}.html"),
                pdf_path=os.path.join(output_base_path, f"{trip_name}.pdf"),
                output_image_path=os.path.join(output_base_path, f"{trip_name}-files"),
                pdf_screenshot_path=os.path.join(output_base_path, f"{trip_name}1.png"),
                leg_plans_path=os.path.join(output_base_path, f"{trip_name}-leg-plans")
            )
            for path, subdirs, files in os.walk(bush_trip_path):
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
            little_nav_map.generate_lnm_file(trip_desc.lnmpln_path)

            # create leg plans
            msfs_plan = MSFSPlan(bush_trip_xml_parser)
            msfs_plan.create_leg_plans(trip_desc.leg_plans_path)

            zipf.write(trip_desc.pdf_path, os.path.basename(trip_desc.pdf_path))
            zipf.write(trip_desc.lnmpln_path, os.path.basename(trip_desc.lnmpln_path))
            zipf.write(trip_desc.leg_plans_path, os.path.basename(trip_desc.leg_plans_path))
            for leg_plan in msfs_plan.plan_files:
                zipf.write(leg_plan, os.path.join(os.path.basename(trip_desc.leg_plans_path), os.path.basename(leg_plan)))

        print(f"writing zip file {zip_path}")
        zipf.close()

asyncio.run(main())