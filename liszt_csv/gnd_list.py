from csv import DictReader, writer
import re

ID_PATTERN = ' \d\d\d\d\d\d*-?\d?X?'
FIND_PATTERN = ID_PATTERN + ' *]'

def parse_csv(file_name):
    with open(file_name) as file:
        reader = DictReader(file)
        content = [row for row in reader]
    return content

def extract_gnd_ids(table, col_name):
    find_pattern = re.compile(FIND_PATTERN)
    gnd_ids = []
    for row in table:
        for found_pattern in find_pattern.findall(row[col_name]):
            found_id = found_pattern.replace(']', '').strip()
            gnd_ids += [ found_id ]
            if len(found_id) < 5:
                print (row[col_name])

    return gnd_ids

def write_csv(content, file_name):
    with open(file_name, 'w') as file:
        content_writer = writer(file)
        for row in content:
            content_writer.writerow([row])

def main():
    FILE_NAME_1 = 'liszt_1a_long.csv'
    FILE_NAME_2 = 'liszt_1b_long.csv'
    FILE_NAME_3 = 'liszt_1c_long.csv'
    FILE_NAME_4 = 'liszt_1d_long.csv'
    FILE_NAME_5 = 'liszt_2_long.csv'
    FILE_NAME_6 = 'liszt_3_long.csv'

    DEDICATION_KEY1 = 'Widmung (diplomatisch)'
    DEDICATION_KEY2 = 'Widmung diplomatisch'
    LOCATION_KEY1 = 'GND-Nr. Ort'
    LOCATION_KEY2 = 'GND Ort'
    LOCATION_KEY3 = 'Ort GND-Nr.'
    NOTES_KEY = 'Notizen zur Quelle (vormals "Beschreibung", bleibt intern)'
    SOURCE_COMMENT_KEY = 'Kommentar zur Quelle (intern)'
    COMMENT_KEY = 'Kommentar'
    PRIVATE_COMMENT_KEY1 = 'Kommentar intern / Fragen (interne Kommunikation)'
    PRIVATE_COMMENT_KEY2 = 'Kommentar intern'
    DATE_LOCATION_KEY = 'Ort ermittelt (normiert)'
    HANDWRITING_KEY1 = 'Schrift (fremder Hand)'
    HANDWRITING_KEY2 = 'Schrift (fremde Hand und Liszt)'
    HANDWRITING_KEY3 = 'Schrift (zS/fremde Hand)'
    HANDWRITING_KEY4 = 'Schrift'
    PUBLISHER_KEY1 = 'Bezug zu Druck: Verlags-GND-Nr.'
    PUBLISHER_KEY2 = 'Verlags GND-Nr.'
    PROVENANCE_KEY_PREFIX = 'Provenienz Station '
    OWNERSHIP_KEY = 'Besitzvermerk (intern)'
    PROVENANCE_KEY = 'Provenienz'

    for filename in [ FILE_NAME_1, FILE_NAME_2, FILE_NAME_3, FILE_NAME_4, FILE_NAME_5, FILE_NAME_6 ]:
        print(filename)
        parsed_csv = parse_csv(filename)

        if PROVENANCE_KEY in parsed_csv[0]:
            gnd_ids = extract_gnd_ids(parsed_csv, PROVENANCE_KEY)
        if DEDICATION_KEY1 in parsed_csv[0]:
            gnd_ids = extract_gnd_ids(parsed_csv, DEDICATION_KEY1)
        if DEDICATION_KEY2 in parsed_csv[0]:
            gnd_ids = extract_gnd_ids(parsed_csv, DEDICATION_KEY2)

        if HANDWRITING_KEY1 in parsed_csv[0]:
            gnd_ids += extract_gnd_ids(parsed_csv, HANDWRITING_KEY1)
        if HANDWRITING_KEY2 in parsed_csv[0]:
            gnd_ids += extract_gnd_ids(parsed_csv, HANDWRITING_KEY2)
        if HANDWRITING_KEY3 in parsed_csv[0]:
            gnd_ids += extract_gnd_ids(parsed_csv, HANDWRITING_KEY3)
        if HANDWRITING_KEY4 in parsed_csv[0]:
            gnd_ids += extract_gnd_ids(parsed_csv, HANDWRITING_KEY4)

        for i in range(4):
            if PROVENANCE_KEY_PREFIX + str(i+1) in parsed_csv[0]:
                gnd_ids += extract_gnd_ids(parsed_csv, PROVENANCE_KEY_PREFIX + str(i+1))

        if DATE_LOCATION_KEY in parsed_csv[0]:
            gnd_ids += extract_gnd_ids(parsed_csv, DATE_LOCATION_KEY)
        gnd_ids += extract_gnd_ids(parsed_csv, NOTES_KEY)

        if COMMENT_KEY in parsed_csv[0]:
            gnd_ids += extract_gnd_ids(parsed_csv, COMMENT_KEY)
        if SOURCE_COMMENT_KEY in parsed_csv[0]:
            gnd_ids += extract_gnd_ids(parsed_csv, SOURCE_COMMENT_KEY)
        if OWNERSHIP_KEY in parsed_csv[0]:
            gnd_ids += extract_gnd_ids(parsed_csv, OWNERSHIP_KEY)

        if PRIVATE_COMMENT_KEY1 in parsed_csv[0]:
            gnd_ids += extract_gnd_ids(parsed_csv, PRIVATE_COMMENT_KEY1)
        if PRIVATE_COMMENT_KEY2 in parsed_csv[0]:
            gnd_ids += extract_gnd_ids(parsed_csv, PRIVATE_COMMENT_KEY2)

        if LOCATION_KEY1 in parsed_csv[0]:
            gnd_ids += [
                    item.strip()
                    for row in parsed_csv if row[LOCATION_KEY1] != ''
                    for item in row[LOCATION_KEY1].split('|')
                ]
        if LOCATION_KEY2 in parsed_csv[0]:
            gnd_ids += [
                    item.strip()
                    for row in parsed_csv if row[LOCATION_KEY2] != ''
                    for item in row[LOCATION_KEY2].split('|')
                ]
        if PUBLISHER_KEY1 in parsed_csv[0]:
            gnd_ids += [
                    item.strip()
                    for row in parsed_csv if row[PUBLISHER_KEY1] != ''
                    for item in row[PUBLISHER_KEY1].split('|')
                ]
        if PUBLISHER_KEY2 in parsed_csv[0]:
            gnd_ids += [
                    item.strip()
                    for row in parsed_csv if row[PUBLISHER_KEY2] != ''
                    for item in row[PUBLISHER_KEY2].split('|')
                ]

    out_gnd_ids = []
    for gnd_id in gnd_ids:
        if gnd_id not in out_gnd_ids:
            out_gnd_ids += [ gnd_id ]

    write_csv(out_gnd_ids, 'gnd_ids.csv')

if __name__ == '__main__':
    main()
