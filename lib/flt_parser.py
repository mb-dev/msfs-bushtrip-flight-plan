from configparser import ConfigParser
from dataclasses import dataclass
from dms2dec.dms_convert import dms2dec
from lib.localization_strings import LocalizationStrings


@dataclass
class POIDesc:
    name: str
    lat: float
    orig_lat: str
    lon: float
    orig_lon: str


def fix_lat_lon(str):
    return str[1:] + str[0]


# flt files contain the names the flight plan assigns to waypoints, such as POI1, or airport codes
# we use it to match waypoints with the name assigned in the flight plan
class FltParser:
    def __init__(self, file_path: str, localization_strings: LocalizationStrings):
        config = ConfigParser()
        config.read(file_path)

        self.title_tt = config["Main"]["Title"]
        self.description_tt = config["Main"]["Description"]
        self.briefing_tt = config["Briefing"]["BriefingText"]
        self.poi_to_names_queue = {}

        for key, value in config.items('ATC_ActiveFlightPlan.0'):
            if key.startswith("waypoint"):
                parts = value.split(",")
                poi = parts[1].strip()
                orig_lat = parts[5].strip()
                lat = dms2dec(fix_lat_lon(orig_lat))
                orig_lon = parts[6].strip()
                lon = dms2dec(fix_lat_lon(orig_lon))

                if poi not in self.poi_to_names_queue:
                    self.poi_to_names_queue[poi] = []

                if parts[3].strip().startswith("TT"):
                    translation_key = parts[3].strip().split(":")[1]
                    self.poi_to_names_queue[poi].append(POIDesc(localization_strings.translation_for(translation_key), lat, orig_lat, lon, orig_lon))
                else:
                    self.poi_to_names_queue[poi].append(POIDesc(parts[3].strip(), lat, orig_lat, lon, orig_lon))

    def pop_next_name_for_poi(self, poi: str) -> POIDesc:
        return self.poi_to_names_queue[poi].pop(0)

    def get_next_name_for_poi(self, poi: str) -> POIDesc:
        return self.poi_to_names_queue[poi][0]