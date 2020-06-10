import csv
import json


#function to get all headers in DLCS export csv and then add three from eureka csv
def get_headers(file_name):
    with open(file_name, 'r', newline='') as f:
        r = csv.reader(f, delimiter=',')
        headers = next(r)
        headers.extend(['Description.tableOfContents','JSON', 'Metadata Only', 'Conceptual Work'])
        return headers

#merges two dictionaries together
def Merge(dict1, dict2): 
    res = {**dict1, **dict2} 
    return res 

dlcs_export = 'minasian_dlcs_export.csv'
works_dict = {}

cursor = csv.DictReader(open(dlcs_export),
    delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

for row in cursor:
    json_data = [json.dumps(row)]
    item_ark = row['Item ARK']
    parent_ark = row['Parent ARK']
    object_type = row['Object Type']
    pagination = row['viewingHint']
    sequence = row['Item Sequence']
    description = row['Description.abstract']
    title = row['Title']
    status = row['Item Status']
    file_name = row['File Name']

    works_dict[item_ark] = {
            'Parent ARK': parent_ark,
            'Object Type': object_type,
            'JSON': json_data,
            'Conceptual Work' : '',
            'Metadata Only': '',
            'Item Status': status
            }
    #checks if a work is a digitized asset based viewingHint value
    if object_type == 'Work':
        if pagination == '':
            works_dict[item_ark]['Metadata Only'] = 'Yes'
        else:
            works_dict[item_ark]['Metadata Only'] = 'No'  

    #checks if a ChildWork is really a conceptual work
    #create a table of contents key and value to later be merged by parent ark            
    if object_type == 'ChildWork':
        if file_name == '':
            works_dict[item_ark]['Conceptual Work'] = 'Yes'
            if description != '':
                works_dict[item_ark]['Description.tableOfContents'] = 'Title: {}; {}'.format(title, description)
            elif description == '':
                works_dict[item_ark]['Description.tableOfContents'] = 'Title: {}'.format(title)
        elif sequence != '':
            works_dict[item_ark]['Conceptual Work'] = 'No'
            works_dict[item_ark]['Object Type'] = 'Page'

    #change Needs Review to completed for visibility after Samvera ingest
    if status == 'Needs Review':
        works_dict[item_ark]['Item Status'] = 'Completed'

for item_ark in works_dict.keys():
    if works_dict[item_ark]['Conceptual Work'] == 'Yes':
        parent_ark = works_dict[item_ark]['Parent ARK']
        text_value = works_dict[item_ark]['Description.tableOfContents']
        if 'Description.tableOfContents' in works_dict[parent_ark]:
            if text_value != '' and text_value not in works_dict[parent_ark]['Description.tableOfContents']:
                works_dict[parent_ark]['Description.tableOfContents'] = '{0}|~|{1}'.format(
                            works_dict[parent_ark]['Description.tableOfContents'],
                            text_value
                            )
        else:
            works_dict[parent_ark]['Description.tableOfContents'] = text_value

#new csv for original csv plus new flags
with open('minasian_dlcs_new_columns.csv', 'w') as out:
    writer = csv.DictWriter(out, fieldnames=get_headers(dlcs_export))
    writer.writeheader()
    cursor = csv.DictReader(open(dlcs_export),
    delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
    for row in cursor:
        for item_ark in works_dict.keys():
            if row['Item ARK'] == item_ark:
                new_row = Merge(row, works_dict[item_ark])
                writer.writerow(new_row)
            else:
                pass

#new csv for digitized works
with open('minasian_digitized_works.csv', 'w') as out:
    writer = csv.DictWriter(out, fieldnames=get_headers(dlcs_export))
    writer.writeheader()
    cursor = csv.DictReader(open(dlcs_export),
    delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
    for row in cursor:
        for item_ark in works_dict.keys():
            if works_dict[item_ark]['Object Type'] == 'Work':
                if row['Item ARK'] == item_ark:
                    if works_dict[item_ark]['Metadata Only'] == 'No':
                        new_row = Merge(row, works_dict[item_ark])
                        writer.writerow(new_row)
                else:
                    pass

#new csv with metadata only works
with open('minasian_metadata_works.csv', 'w') as out:
    writer = csv.DictWriter(out, fieldnames=get_headers(dlcs_export))
    writer.writeheader()
    cursor = csv.DictReader(open(dlcs_export),
    delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
    for row in cursor:
        for item_ark in works_dict.keys():
            if row['Item ARK'] == item_ark:
                if works_dict[item_ark]['Object Type'] == 'Work':
                    if works_dict[item_ark]['Metadata Only'] == 'Yes':
                        new_row = Merge(row, works_dict[item_ark])
                        writer.writerow(new_row)
            else:
                pass
               
#new csv with conceptual works (at childwork level)
with open('minasian_childworks_conceptual_works.csv', 'w') as out:
    writer = csv.DictWriter(out, fieldnames=get_headers(dlcs_export))
    writer.writeheader()
    cursor = csv.DictReader(open(dlcs_export),
    delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
    for row in cursor:
        for item_ark in works_dict.keys():
            if works_dict[item_ark]['Conceptual Work'] == 'Yes':
                if row['Item ARK'] == item_ark:
                    new_row = Merge(row, works_dict[item_ark])
                    writer.writerow(new_row)
        else:
            pass

#new csv for each manuscript's pages
for item_ark in works_dict.keys():
    if works_dict[item_ark]['Object Type'] == 'Work':
        if works_dict[item_ark]['Metadata Only'] == 'No':
            pages_file_name = str((str(item_ark)).replace('ark:/', '').replace('/', '')+'_pages.csv')
            with open(pages_file_name, 'w') as out:
                writer = csv.DictWriter(out, fieldnames=get_headers(dlcs_export))
                writer.writeheader()
                cursor = csv.DictReader(open(dlcs_export),
                delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
                for row in cursor:
                    if row['Parent ARK'] == item_ark and row['Item Sequence'] != '' and row['Object Type'] == 'ChildWork' and row['File Name'] != '':
                        childwork_ark = row['Item ARK']
                        new_row = Merge(row, works_dict[childwork_ark])
                        writer.writerow(new_row)
                    else:
                        pass
