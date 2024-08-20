import sys,os
os.chdir('/home/app-pimd/tfm2024/APP_WAREHOUSE')
sys.path.append(os.getcwd())

from api.authentication import Authentication

a = Authentication()
print(a.register_user("tfm2024")) # Store api-key
a.assign_role("tfm2024", "admin")