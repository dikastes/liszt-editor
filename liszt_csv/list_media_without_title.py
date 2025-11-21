import csv

envelope_titles = []
head_titles = []
with open('liszt_1d_long.csv') as file:
    csv_reader = csv.DictReader(file)
    envelope_titles = [
        {
            'title': row['Titelei Umschlag und/oder Titelblatt (diplomatisch)'],
            'medium': medium,
            'signature': row['Signatur, neu'],
            'norm_title': row['Titel (normiert, nach MGG)']
        }
        for row
        in csv_reader
        if (medium := row['Autor Titelei (Liszt egh.)'])
    ]

with open('liszt_1d_long.csv') as file:
    csv_reader = csv.DictReader(file)
    head_titles = [
        {
            'title': row['Kopftitel'],
            'medium': medium,
            'signature': row['Signatur, neu'],
            'norm_title': row['Titel (normiert, nach MGG)']
        }
        for row
        in csv_reader
        if (medium := row['Autor Kopftitel (Liszt egh.)'])
    ]
    print(head_titles)

print('== 1D ==')
for title in envelope_titles:
    if not title['title']:
        print(f"{title['signature']}, {title['norm_title']}: kein Umschlagtitel für Schreibmittel {title['medium']}")
for title in head_titles:
    if not title['title']:
        print(f"{title['signature']}, {title['norm_title']}: kein Kopftitel für Schreibmittel {title['medium']}")

with open('liszt_2_long.csv') as file:
    csv_reader = csv.DictReader(file)
    envelope_titles = [
        {
            'title': row['Titelei Umschlag und/oder Titelblatt (diplomatisch)'],
            'medium': medium,
            'signature': row['Signatur, neu'],
            'norm_title': row['Titel (normiert, nach MGG)']
        }
        for row
        in csv_reader
        if (medium := row['Schreiber Titelei'])
    ]

with open('liszt_2_long.csv') as file:
    csv_reader = csv.DictReader(file)
    head_titles = [
        {
            'title': row['Kopftitel'],
            'medium': medium,
            'signature': row['Signatur, neu'],
            'norm_title': row['Titel (normiert, nach MGG)']
        }
        for row
        in csv_reader
        if (medium := row['Schreiber Kopftitel'])
    ]

print('== 2 ==')
for title in envelope_titles:
    if not title['title']:
        print(f"{title['signature']}, {title['norm_title']}: kein Umschlagtitel für Schreibmittel {title['medium']}")
for title in head_titles:
    if not title['title']:
        print(f"{title['signature']}, {title['norm_title']}: kein Kopftitel für Schreibmittel {title['medium']}")
