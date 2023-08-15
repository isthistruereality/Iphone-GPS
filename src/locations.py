import glob
import os
from PIL import Image
from pillow_heif import register_heif_opener

def get_exif(filename):
    image = Image.open(filename)
    # Verify if image is corrupt, then grab the GPS exif data.  0x8825 is the EXIF GPS data tag.
    image.verify()
    return image.getexif().get_ifd(0x8825)


def get_geotagging(exif):
    geo_tagging_info = {}
    if not exif:
        raise ValueError("No EXIF metadata found")
    else:
        gps_keys = ['GPSVersionID', 'GPSLatitudeRef', 'GPSLatitude', 'GPSLongitudeRef', 'GPSLongitude',
                    'GPSAltitudeRef', 'GPSAltitude', 'GPSTimeStamp', 'GPSSatellites', 'GPSStatus', 'GPSMeasureMode',
                    'GPSDOP', 'GPSSpeedRef', 'GPSSpeed', 'GPSTrackRef', 'GPSTrack', 'GPSImgDirectionRef',
                    'GPSImgDirection', 'GPSMapDatum', 'GPSDestLatitudeRef', 'GPSDestLatitude', 'GPSDestLongitudeRef',
                    'GPSDestLongitude', 'GPSDestBearingRef', 'GPSDestBearing', 'GPSDestDistanceRef', 'GPSDestDistance',
                    'GPSProcessingMethod', 'GPSAreaInformation', 'GPSDateStamp', 'GPSDifferential']

        for k, v in exif.items():
            try:
                geo_tagging_info[gps_keys[k]] = str(v)
            except IndexError:
                pass
        print(geo_tagging_info)
        return geo_tagging_info

def dms_to_decimal(dms_string, ref):
    # The meta data initially comes in DMS (Decimals, minutes, seconds) form. For usability, we convert to single decimal degree.
    degrees, minutes, seconds = map(float, dms_string[1:-1].split(', '))
    decimal_value = degrees + minutes / 60 + seconds / 3600
    # Depending on the hemisphere, we must assign + or - value to the degrees.
    if ref in ["W", "S"]:
        decimal_value = -decimal_value
    return decimal_value


def process_image(image_path):
    register_heif_opener()
    image_info = get_exif(image_path)
    results = get_geotagging(image_info)

    decimal_longitude = dms_to_decimal(results['GPSLongitude'], results['GPSLongitudeRef'])
    decimal_latitude = dms_to_decimal(results['GPSLatitude'], results['GPSLatitudeRef'])
    decimal_altitude = results['GPSAltitude']

    return decimal_latitude, decimal_longitude, decimal_altitude

def process_all_heic_files(folder_path):
    metadata_files = {}
    no_metadata_files = []
    heic_files = glob.glob(f'{folder_path}/*.HEIC')

    for heic_file in heic_files:
        base_filename = os.path.basename(heic_file)  # Get the base filename
        try:
            latitude, longitude, altitude = process_image(heic_file)
            metadata_files[base_filename] = {'latitude': latitude, 'longitude': longitude, 'altitude': altitude}
        except ValueError as e:
            print(f'File: {base_filename} - {e}\n')
            no_metadata_files.append(base_filename)  # Add the base filename to the no_metadata_files list

    return metadata_files, no_metadata_files

folder_path = r"C:\Users\Jake\Desktop\HACKER\hi\images"  # Update with the path to your folder containing HEIC files
results_with_metadata, results_without_metadata = process_all_heic_files(folder_path)

print("Files with GPS Metadata:")
print(results_with_metadata)
print("\nFiles without GPS Metadata:")
print(results_without_metadata)

