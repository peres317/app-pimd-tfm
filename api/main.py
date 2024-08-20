from gevent import monkey; monkey.patch_all()

import sys,os
os.chdir('/home/app-pimd/tfm2024/APP_WAREHOUSE')
sys.path.append(os.getcwd())

from controller.controller import LoadController as db
from controller.controller import AdminController as admin

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status, Request, Query
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer, HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
import json
from threading import Thread, Lock
import typing as t
from time import time
from datetime import datetime

from api.models import *
from api.authentication import Authentication
from api.documentation import description, title, version, contact, license_info

from api.v2 import v2

###########
# THREADS #
###########

# Single threads
aosp_thread = Thread()
app_candidates_thread = Thread()
random_n_download_thread = Thread()
random_n_candidates_thread = Thread()
apply_metrics_thread = Thread()

# Current threads
MAX_LIVE_UPLOAD_THREADS = 1
live_upload_lock: Lock = Lock()
live_upload_threads: list[Thread] = []
credentials_lock: Lock = Lock()


##################
# AUTHENTICATION #
##################

oauth2_scheme = HTTPBearer()

def api_key_expert_auth(
    api_key: t.Optional[HTTPAuthorizationCredentials] = Depends(oauth2_scheme)) -> str:
    """Authenticates a expert by its api key.

    Args:
        api_key (str, optional): Api key. Defaults to Depends(oauth2_scheme).

    Raises:
        HTTPException: Api key not valid.

    Returns:
        str: Expert name.
    """
    auth = Authentication()
    if not auth.get_roles(api_key.credentials):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    if "expert" not in auth.get_roles(api_key.credentials):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    return auth.get_user_name(api_key.credentials)

def api_key_admin_auth(
    api_key: t.Optional[HTTPAuthorizationCredentials] = Depends(oauth2_scheme)):
    """Authenticates a admin user by its api key.

    Args:
        api_key (str, optional): Admin api key. Defaults to
            Depends(oauth2_scheme).

    Raises:
        HTTPException: Api key not valid.
    """
    auth = Authentication()
    if not auth.get_roles(api_key.credentials):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    if "admin" not in auth.get_roles(api_key.credentials):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

#######
# API #
#######

ROOT_PATH = "/api"

api = FastAPI(
    title="AppWarehouse",
    description=description,
    # summary="Warehouse access API.", ?
    version=version,
    # terms_of_service="# TODO",
    contact=contact,
    license_info=license_info,
    openapi_url=None, # Disable openapi
    docs_url=None, # Disable docs (Swagger UI)
    redoc_url=None)#, # Disable redoc)


#################
# DOCUMENTATION #
#################

# Common
security = HTTPBasic()

# User
user_tag = [
    {
        "name": "User",
        "description": "User's available operations."
    }
]
USER_PATHS = [
    "/get/app/hash",
    "/get/app/package",
    "/post/app/package"
]
user_description = """
## User

You will be able to:

* Download app metadata stored on the warehouse.
* Request to upload an app to the warehouse.

"""

@api.get("/docs",
         include_in_schema=False)
async def get_user_docs():
    return get_swagger_ui_html(
        openapi_url=ROOT_PATH + "/openapi.json",
        title="docs",
        swagger_ui_parameters={
            "defaultModelsExpandDepth": -1,
            "displayRequestDuration": True
        }
    )

@api.get("/openapi.json",
         include_in_schema=False)
async def get_user_openapi():
    user_routes = [route for route in api.routes if route.path in USER_PATHS]

    docs = get_openapi(
        title=api.title,
        description=api.description + user_description,
        version=api.version,
        contact=api.contact,
        license_info=api.license_info,
        routes=user_routes,
        tags=user_tag
    )

    docs["servers"] = [{"url": ROOT_PATH}]

    return docs

# Expert
expert_tag = [
    {
        "name": "Expert",
        "description": "Expert's available operations."
    }
]
EXPERT_PATHS = [
    "/expert/get/name",
    "/expert/post/score"
]
expert_description = """
## Expert

You will be able to:

* Execute all User associated operations.
* Get your associated name.
* Upload an app score to the warehouse.

"""

def expert_user(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.password == "docmaster":
        return
    auth = Authentication()
    if not auth.get_roles(credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Basic"}
        )
    if "expert" not in auth.get_roles(credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Basic"}
        )

@api.get("/expert/docs",
         dependencies=[Depends(expert_user)],
         include_in_schema=False)
async def get_user_docs():
    return get_swagger_ui_html(
        openapi_url=ROOT_PATH + "/expert/openapi.json",
        title="docs",
        swagger_ui_parameters={
            "defaultModelsExpandDepth": -1,
            "displayRequestDuration": True
        }
    )

@api.get("/expert/openapi.json",
         dependencies=[Depends(expert_user)],
         include_in_schema=False)
async def get_user_openapi():
    user_routes = [route for route in api.routes if route.path in USER_PATHS]
    expert_routes = [route for route in api.routes if route.path in EXPERT_PATHS]

    docs = get_openapi(
        title=api.title,
        description=api.description + user_description + expert_description,
        version=api.version,
        contact=api.contact,
        license_info=api.license_info,
        routes=user_routes + expert_routes,
        tags=user_tag + expert_tag
    )

    docs["servers"] = [{"url": ROOT_PATH}]

    return docs

# Admin

admin_tag = [
    {
        "name": "Admin",
        "description": "Administrator operations."
    }
]
ADMIN_PATHS = [
    "/admin/post/expert",
    "/admin/update/aosp",
    "/admin/update/aosp/status",
    "/admin/clean_cache",
    "/admin/update/app_candidates",
    "/admin/update/app_candidates/status",
    "/admin/upload/n_random_apps",
    "/admin/upload/n_random_apps/status",
    "/admin/upload/n_random_app_candidates",
    "/admin/upload/n_random_app_candidates/status",
    "/admin/update/apply_metrics",
    "/admin/update/apply_metrics/status",
    "/admin/delete/user"
]
admin_description = """
## Admin

You will be able to:

* Execute all User associated operations.
* Execute all Expert associated operations.
* Register new experts in the warehouse.
* Request to update the AOSP data in the warehouse (Android permission and group permission).
* View the status of the AOSP update.
* Clean all temporal data (app candidates list, AOSP data cache, partial downloads...).
* Request to update the app candidates list in the warehouse (most important apps according to Play Store).
* View the status of the app candidates update.
* Request to upload an arbitrary number of random apps to the warehouse.
* View the status of the n random apps upload.
* Request to upload an arbitrary number of random apps from the candidates to the warehouse.
* View the status of the n random apps from the candidates upload.
* Request to apply all stored metrics to all apps.
* View the status of the apply all metrics request.
* Revoke non admin user.

"""

def admin_user(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.password == "docmaster":
        return
    auth = Authentication()
    if not auth.get_roles(credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Basic"}
        )
    if "admin" not in auth.get_roles(credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Basic"}
        )

@api.get("/admin/docs",
         dependencies=[Depends(admin_user)],
         include_in_schema=False)
async def get_admin_docs():
    return get_swagger_ui_html(
        openapi_url=ROOT_PATH + "/admin/openapi.json",
        title="docs",
        swagger_ui_parameters={
            "defaultModelsExpandDepth": -1,
            "displayRequestDuration": True
        }
    )

@api.get("/admin/openapi.json",
         dependencies=[Depends(admin_user)],
         include_in_schema=False)
async def get_admin_openapi():
    user_routes = [route for route in api.routes if route.path in USER_PATHS]
    expert_routes = [route for route in api.routes if route.path in EXPERT_PATHS]
    admin_routes = [route for route in api.routes if route.path in ADMIN_PATHS]

    docs = get_openapi(
        title=api.title,
        description=api.description + user_description + expert_description + admin_description,
        version=api.version,
        contact=api.contact,
        license_info=api.license_info,
        routes=user_routes + expert_routes + admin_routes,
        tags=user_tag + expert_tag + admin_tag
    )
    
    docs["servers"] = [{"url": ROOT_PATH}]

    return docs


#####################
# API FUNCTIONALITY #
#####################

@api.get("/get/app/hash",
         status_code=status.HTTP_200_OK,
         summary="Download app metadata by its hash",
         response_model=AppElement,
         response_description="App metadata",
         responses={
             404: {
                 "model": Message,
                 "description": "App not found Error"
             },
         },
         tags=["User"])
async def get_app_by_hash(hash: str = Query(description="SHA256 hash of the app to download")) -> dict:
    """Download app metadata by its sha256 hash of the package file (e.g. _4e2d2f9383c46905bf2b67acd7921c7d9b2f663191f29a8c451fcfe5e66d20c5_).
    """
    app_data = db.get_app_by_hash(hash)
    if not app_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="App not found"
        )

    return app_data

@api.get("/get/app/package",
         status_code=status.HTTP_200_OK,
         summary="Download app metadata by its package name",
         response_model=AppElement,
         response_description="App metadata",
         responses={
             404: {
                 "model": Message,
                 "description": "App not found Error"
             },
         },
         tags=["User"])
async def get_app_by_package(package: str = Query(description="package name of the app to download")) -> dict:
    """Download app metadata by its package name (e.g. _net.universia.uva_).
    """
    app_data = db.get_app_by_package(package)
    if not app_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="App not found"
        )

    return app_data

@api.post("/post/app/package",
          status_code=status.HTTP_200_OK,
          summary="Request app upload by its package name",
          response_model=Message,
          response_description="Request status (busy, requested)",
          tags=["User"])
async def upload_app_by_package(package: Package) -> dict:
    """Request app upload by its package name (e.g. _net.universia.uva_).

    Request status:
    * **busy**: request is not going to be performed.
    * **requested**: request is going to be performed.
    """
    with live_upload_lock:
        # Update list of threads
        global live_upload_threads
        live_upload_threads = [t for t in live_upload_threads if t.is_alive()]

        response = {"detail": ""}

        if len(live_upload_threads) == MAX_LIVE_UPLOAD_THREADS:
            response["detail"] = "busy"
        else:
            thread = Thread(target=db.request_app_upload,
                            args=[package.package])
            thread.start()

            live_upload_threads.append(thread)

            response["detail"] = "requested"

        return response

# TODO: admin functionality?
@api.get("/post/app/package/status",
         tags=["User"])
async def upload_app_by_package_status() -> dict:
    """Return status of upload app request.

    Returns:
        dict: {n_threads}
    """
    with live_upload_lock:
        # Update list of threads
        global live_upload_threads
        live_upload_threads = [t for t in live_upload_threads if t.is_alive()]

        return {"n_threads": len(live_upload_threads)}


############################
# EXPERT API FUNCTIONALITY #
############################

@api.get("/expert/get/name",
         dependencies=[Depends(api_key_expert_auth)],
         status_code=status.HTTP_200_OK,
         summary="Get current expert name",
         response_model=Message,
         response_description="Current expert name",
         tags=["Expert"])
async def get_current_expert_name(current_expert: t.Annotated[str, Depends(api_key_expert_auth)]) -> dict:
    """Get current expert name.
    """
    return {"detail": current_expert}

@api.post("/expert/post/score",
          dependencies=[Depends(api_key_expert_auth)],
          status_code=status.HTTP_200_OK,
          summary="Upload an app score",
          response_model=Message,
          response_description="Upload status (successful, unexpected error)",
          responses={
             404: {
                 "model": Message,
                 "description": "App not found Error"
             },
         },
          tags=["Expert"])
async def upload_expert_score(
    req: ExpertScore,
    current_expert: t.Annotated[str, Depends(api_key_expert_auth)]) -> dict:
    """Uploads an score to an existing app by its hash. Score must be [0,10] normalized.

    Request status:
    * **successful**: new score uploaded.
    * **unexpected error**: new score could not be loaded contact to administrator.
    """
    response = {"detail": "requested"}

    # Check if app exists
    app_data = db.get_app_by_hash(req.app_hash)
    if not app_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="App not found"
        )

    # Check if score normalized
    if req.value < 0 or req.value > 10:
        return JSONResponse(
            {
                "detail": [
                    {
                        "loc": [
                            "body",
                            "value"
                        ],
                        "msg": "value must be [0, 10] normalized",
                        "type": "value_error.normalization"
                    }
                ]
            }, status_code=422)

    json_score = {
        "Score": {
            "value": req.value,
            "rank_name": current_expert,
            "app_hash": req.app_hash
        }
    }
    try:
        result = admin.upload_json(json.dumps(json_score))
        response = {"detail": "successful"}

        if result["row_count"] == 0:
            response = {"detail": "error score not uploaded. Maybe already on warehouse?"}
    except Exception:
        response = {"detail": "unexpected error"}

    return response


###########################
# ADMIN API FUNCTIONALITY #
###########################

@api.post("/admin/post/expert",
          dependencies=[Depends(api_key_admin_auth)],
          status_code=status.HTTP_200_OK,
          summary="Register new expert",
          response_model=Message,
          response_description="Register status (api_key, unexpected error)",
          tags=["Admin"])
async def upload_new_expert(
    user_name: str = Query(description="name of the expert (id)"),
    source: str = Query(description="source of the expert (email, website...)")) -> dict:
    """Registers a new expert in the warehouse.

    Request status:
    * **api_key**: new expert uploaded api_key.
    * **unexpected error**: new expert could not be loaded.
    """
    response = {"detail": "requested"}

    auth = Authentication()
    with credentials_lock:
        api_key = auth.register_user(user_name)
    if not api_key:
        response = {"detail": "User name not valid."}
        return response

    auth.assign_role(user_name, "expert")

    privacy_rank = {
        "PrivacyRank": {
            "name": user_name,
            "source": source,
            "timestamp": datetime.fromtimestamp(time()).strftime('%Y-%m-%d %H:%M:%S'),
            "permission_ranks_list": [],
            "app_scores_list": []
        }
    }

    try:
        result = admin.upload_json(json.dumps(privacy_rank))
        response = {"detail": "Api key: " + api_key}
    except Exception:
        response = {"detail": "unexpected error"}
###########################
# ADMIN API FUNCTIONALITY #
###########################
    return response

@api.get("/admin/update/aosp",
         dependencies=[Depends(api_key_admin_auth)],
         status_code=status.HTTP_200_OK,
         summary="Request update AOSP data",
         response_model=Message,
         response_description="Request status (busy, requested)",
         tags=["Admin"])
async def update_aosp_data() -> dict:
    """Request to update AOSP data. Only one update can run at a time.

    Request status:
    * **busy**: Request update AOSP data is already running.
    * **requested**: Request update AOSP data is going to be performed.
    """
    response = {"detail": ""}

    global aosp_thread
    if aosp_thread.is_alive():
        response["detail"] = "busy"
    else:
        aosp_thread = Thread(target=admin.update_aosp_data, name="Aosp")
        aosp_thread.start()

        response["detail"] = "requested"

    return response

@api.get("/admin/update/aosp/status",
         dependencies=[Depends(api_key_admin_auth)],
         status_code=status.HTTP_200_OK,
         summary="Get request update AOSP data status",
         response_model=Message,
         response_description="Request status (busy, inactive)",
         tags=["Admin"])
async def update_aosp_data_status() -> dict:
    """Return status of AOSP data update request.

    Request status:
    * **busy**: Request update AOSP data is running.
    * **inactive**: Request update AOSP data is not running.
    """
    response = {"detail": ""}
    if aosp_thread.is_alive():
        response["detail"] = "busy"
    else:
        response["detail"] = "inactive"

    return response

@api.get("/admin/clean_cache",
         dependencies=[Depends(api_key_admin_auth)],
         status_code=status.HTTP_200_OK,
         summary="Clean temporal directories",
         response_model=Message,
         response_description="Number of files deleted",
         tags=["Admin"])
async def clean_cache() -> dict:
    """Cleans cache. Be careful when to execute this can delete in use files.
    """
    return admin.clean_cache()

@api.get("/admin/update/app_candidates",
         dependencies=[Depends(api_key_admin_auth)],
         status_code=status.HTTP_200_OK,
         summary="Request update app candidates",
         response_model=Message,
         response_description="Request status (busy, requested)",
         tags=["Admin"])
async def update_app_candidates() -> dict:
    """Request to update app candidates (most important apps according to Play
    Store). Only one update can run at a time.

    Request status:
    * **busy**: Request update app candidates is already running.
    * **requested**: Request update app candidates is going to be performed.
    """
    response = {"detail": ""}

    global app_candidates_thread
    if app_candidates_thread.is_alive():
        response["detail"] = "busy"
    else:
        app_candidates_thread = Thread(target=admin.get_app_candidates,
                                       name="App candidates")
        app_candidates_thread.start()

        response["detail"] = "requested"

    return response

@api.get("/admin/update/app_candidates/status",
         dependencies=[Depends(api_key_admin_auth)],
         status_code=status.HTTP_200_OK,
         summary="Get request update app candidates status",
         response_model=Message,
         response_description="Request status (busy, inactive)",
         tags=["Admin"])
async def update_app_candidates_status() -> dict:
    """Return status of app candidates update request.

    Request status:
    * **busy**: Request update app candidates is running.
    * **inactive**: Request update app candidates is not running.
    """
    response = {"detail": ""}
    if app_candidates_thread.is_alive():
        response["detail"] = "busy"
    else:
        response["detail"] = "inactive"

    return response

@api.get("/admin/upload/n_random_apps",
         dependencies=[Depends(api_key_admin_auth)],
         status_code=status.HTTP_200_OK,
         summary="Request upload n random apps",
         response_model=Message,
         response_description="Request status (busy, requested)",
         tags=["Admin"])
async def get_n_random_apps(
    n_apps: int = Query(description="number of apps to upload", le=20)) -> dict:
    """Request to upload n_apps random apps to the warehouse.

    Request status:
    * **busy**: Request upload n random apps is already running.
    * **requested**: Request upload n random apps is going to be performed.
    """
    response = {"detail": ""}

    global random_n_download_thread
    if random_n_download_thread.is_alive():
        response["detail"] = "busy"
    else:
        random_n_download_thread = Thread(target=admin.download_random_apps,
                                          name="Androzoo random download",
                                          args=[n_apps])
        random_n_download_thread.start()

        response["detail"] = "requested"

    return response

@api.get("/admin/upload/n_random_apps/status",
         dependencies=[Depends(api_key_admin_auth)],
         status_code=status.HTTP_200_OK,
         summary="Get request upload n random apps status",
         response_model=Message,
         response_description="Request status (busy, inactive)",
         tags=["Admin"])
async def get_n_random_apps_status() -> dict:
    """Return status of n random apps download request.

    Request status:
    * **busy**: Request upload n random apps is running.
    * **inactive**: Request upload n random apps is not running.
    """
    response = {"detail": ""}
    if random_n_download_thread.is_alive():
        response["detail"] = "busy"
    else:
        response["detail"] = "inactive"

    return response

@api.get("/admin/upload/n_random_app_candidates",
         dependencies=[Depends(api_key_admin_auth)],
         status_code=status.HTTP_200_OK,
         summary="Request upload n random apps from candidates",
         response_model=Message,
         response_description="Request status (busy, requested)",
         tags=["Admin"])
async def get_n_random_app_candidates(
    n_apps: int = Query(description="number of apps to upload", le=20)) -> dict:
    """Request to download n_apps apps from candidates.

    Request status:
    * **busy**: Request upload n random apps from candidates is already running.
    * **requested**: Request upload n random apps from candidates is going to be performed.
    """
    response = {"detail": ""}

    global random_n_candidates_thread
    if random_n_candidates_thread.is_alive():
        response["detail"] = "busy"
    else:
        random_n_candidates_thread = Thread(
            target=admin.download_random_apps_from_candidates,
            name="Androzoo random download",
            args=[n_apps])
        random_n_candidates_thread.start()

        response["detail"] = "requested"

    return response

@api.get("/admin/upload/n_random_app_candidates/status",
         dependencies=[Depends(api_key_admin_auth)],
         status_code=status.HTTP_200_OK,
         summary="Get request upload n random apps from candidates status",
         response_model=Message,
         response_description="Request status (busy, inactive)",
         tags=["Admin"])
async def get_n_random_app_candidates_status() -> dict:
    """Return status of n random candidate apps download request.

    Request status:
    * **busy**: Request upload n random apps from candidates is running.
    * **inactive**: Request upload n random apps from candidates is not running.
    """
    response = {"detail": ""}
    if random_n_candidates_thread.is_alive():
        response["detail"] = "busy"
    else:
        response["detail"] = "inactive"

    return response

@api.get("/admin/update/apply_metrics",
         dependencies=[Depends(api_key_admin_auth)],
         status_code=status.HTTP_200_OK,
         summary="Apply all metrics to stored apps request",
         response_model=Message,
         response_description="Request status (busy, requested)",
         tags=["Admin"])
async def apply_metrics() -> dict:
    """Request to apply score metrics to all apps. Only one apply can run at a time.

    Request status:
    * **busy**: Apply all metrics to stored apps request is already running.
    * **requested**: Apply all metrics to stored apps request is going to be performed.
    """
    response = {"detail": ""}

    global apply_metrics_thread
    if apply_metrics_thread.is_alive():
        response["detail"] = "busy"
    else:
        apply_metrics_thread = Thread(
            target=admin.apply_all_metrics,
            name="All metrics")
        apply_metrics_thread.start()

        response["detail"] = "requested"

    return response

@api.get("/admin/update/apply_metrics/status",
         dependencies=[Depends(api_key_admin_auth)],
         status_code=status.HTTP_200_OK,
         summary="Get apply all metrics to stored apps request status",
         response_model=Message,
         response_description="Request status (busy, inactive)",
         tags=["Admin"])
async def get_n_random_app_candidates_status() -> dict:
    """Return status of apply score metrics to all apps request.

    Request status:
    * **busy**: Apply all metrics to stored apps request is running.
    * **inactive**: Apply all metrics to stored apps request is not running.
    """
    response = {"detail": ""}
    if apply_metrics_thread.is_alive():
        response["detail"] = "busy"
    else:
        response["detail"] = "inactive"

    return response

@api.post("/admin/delete/user",
          dependencies=[Depends(api_key_admin_auth)],
          status_code=status.HTTP_200_OK,
          summary="Deletes non admin user",
          response_model=Message,
          response_description="Delete status (successful, error)",
          tags=["Admin"])
async def update_api_key(
    user_name: str = Query(description="name of the user (id)")) -> dict:
    """Deletes a non admin user.

    Request status:
    * **successful**: User deleted.
    * **unexpected error**: user could not be deleted.
    """
    auth = Authentication()
    roles = auth.get_roles_by_user(user_name)
    if "admin" in roles:
        return {"detail": "Could not delete admin user."}

    result = auth.revoke_access(user_name)
    if not result:
        return {"detail": "unexpected error"}

    return {"detail": "successful"}

####################
# v2 FUNCTIONALITY #
####################

api.include_router(v2.router)

if __name__ == '__main__':
    uvicorn.run("api.main:api", port=8080, host='0.0.0.0', workers=1)
