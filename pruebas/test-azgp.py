# {"package_name": [(version_code1, list[hash]), ...]}
app_list = {}
with open("apps.csv") as f:
    lines = f.readlines()

    for line in lines:
        linecontent = line[:-1].split(",")

        package = linecontent[0][1:-1]
        version_code = int(linecontent[1][1:-1])
        app_hash = linecontent[2][1:-1]

        added = False
        if package in app_list.keys():
            for vc, hl in app_list[package]:
                if vc == version_code:
                    hl.append(app_hash)
                    added = True
            if not added:
                app_list[package].append((version_code, [app_hash]))
        else:
            app_list[package] = [(version_code, [app_hash])]
            added = True

from etl.extract.androzoo import AndrozooGP
from etl.load.az_metadata_loader import AzMetadataLoader

az_metadata_list = AndrozooGP().bulk_load_from_index("/media/app-pimd/Data/gp-metadata-full.jsonl.gz", 16881166, app_list)

loader = AzMetadataLoader()
for az_metadata in az_metadata_list:
    print(loader.load_az_metadata(az_metadata))