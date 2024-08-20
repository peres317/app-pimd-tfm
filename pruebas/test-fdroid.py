# from etl.extract.fdroid import FDroid

# f = FDroid()
# f.download_app("org.telegram.messenger")

from controller.controller import LoadController as ld

with open("fdroid-packages.lst") as f:
    packages = f.read()
    packages = packages.split("\n")

for (i, p) in enumerate(packages):
    print(i, p)
    ld.request_app_upload(p)