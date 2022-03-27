from cachier import cachier
from magnetic_field_calculator import MagneticFieldCalculator


@cachier()
def get_waypoint_mag_declination(lat, lon):
    mag_field_calculator = MagneticFieldCalculator()
    result = mag_field_calculator.calculate(
        latitude=lat,
        longitude=lon,
        date='2028-12-31'
    )
    field_value = result['field-value']
    declination =  field_value['declination']['value']

    print(f"request mag declination {lat} {lon}")

    return declination