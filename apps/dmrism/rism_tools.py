import requests
from django.conf import settings
from io import BytesIO
from pymarc.marcxml import parse_xml_to_array

def get_rism_data(rism_id):
    BASE_URL = 'https://muscat.rism.info/data/sources/'
    rism_token = settings.RISM_API_KEY
    headers = {
            "Authorization": f"Bearer {rism_token}"
        }

    try:
        response = requests.get(BASE_URL + rism_id, headers=headers)
        if response.status_code == 401:
            raise Exception("Ungültiger RISM API-Token")
        if response.status_code == 404:
            raise Exception(f"Ungültige RISM-ID: {rism_id}")
    except requests.exceptions.Timeout:
        raise Exception("Netzwerkfehler. Später wieder versuchen.")

    byte_stream = BytesIO(response.content)
    return parse_xml_to_array(byte_stream)[0]
