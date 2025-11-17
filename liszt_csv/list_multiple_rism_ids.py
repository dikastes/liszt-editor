import csv

contents = []
with open('liszt_1d_long.csv') as file:
    csv_reader = csv.DictReader(file)
    contents = [ id for row in csv_reader if (id := row['RISM ID no.']) ]

print('== 1D ==')
ids = []
printed_ids = []
for id in contents:
    if id in ids:
        if id not in printed_ids:
            print(id)
            printed_ids += [ id ]
    else:
        ids += [ id ]

with open('liszt_2_long.csv') as file:
    csv_reader = csv.DictReader(file)
    contents = [ id for row in csv_reader if (id := row['RISM ID no.']) ]

print('== 2 ==')
ids = []
printed_ids = []
for id in contents:
    if id in ids:
        if id not in printed_ids:
            print(id)
            printed_ids += [ id ]
    else:
        ids += [ id ]

