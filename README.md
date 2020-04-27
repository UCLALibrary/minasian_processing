# minasian_processing
Contains a script to break the Minasian collection into many csvs with added flags and json data

# Make a directory and clone this repo
1. $ mkdir minasian
2. $ cd minasian
3. $ git clone https://github.com/UCLALibrary/minasian_processing.git
4. $ cd minasian_processing

# Unzip the csv (this csv name is hardcoded in the script)

# Run the script
$ python3 minasian_processing.py

You will start to see new csv files appear in this directory. The original csv will remain unchanged. 
# New csvs
1. minasian_dlcs_new_columns.csv - Takes original export csv and adds columns for JSON data, a flag if the item is Metadata Only and a flag if the item is a Conceptual Work
2. minasian_digitized_works.csv - A csv with only Works that are digitized (only have pages as children)
3. minasian_metadata_works.csv - A csv with only Works that are metadata only (no pages as children)
4. minasian_childWorks_conceptual_works.csv - A csv with all DLCS object type Work (a conceptual work found within a manuscript)
5. A csv for each digitized work's pages (about 300 csvs for this collection).
