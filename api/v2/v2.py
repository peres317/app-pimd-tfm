from fastapi import APIRouter, Depends, status, Query, HTTPException, UploadFile, File
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from api.documentation import *
from .documentation import *
from .models import *
from ..models import *

from controller.controller import LoadController as db


ROOT_PATH = "/api"


router = APIRouter(
    prefix="/v2",
    tags=["v2"],
    responses={404: {"description": "Not found"}},
)


#####################
# GET DOCUMENTATION #
#####################

@router.get("/docs",
         include_in_schema=False)
async def get_v2_docs():
    return get_swagger_ui_html(
        openapi_url=ROOT_PATH + "/v2/openapi.json",
        title="docs",
        swagger_ui_parameters={
            "defaultModelsExpandDepth": -1,
            "displayRequestDuration": True
        }
    )

@router.get("/openapi.json",
         include_in_schema=False)
async def get_v2_openapi():
    v2_routes = [route for route in router.routes]

    docs = get_openapi(
        title=title,
        description=description + V2_description,
        version=version,
        contact=contact,
        license_info=license_info,
        routes=v2_routes,
        tags=V2_tag
    )

    docs["servers"] = [{"url": ROOT_PATH}]

    return docs


#################
# FUNCTIONALITY #
#################

@router.get("/get/app/versions",
         status_code=status.HTTP_200_OK,
         summary="View all app versions available by its package name",
         response_model=AvailableVersions,
         response_description="All app versions available",
         responses={
             404: {
                 "model": Message,
                 "description": "App not found Error"
             },
         },
         tags=["v2"])
async def get_all_app_versions_by_package(package: str = Query(description="package name of the app to download")) -> dict:
    """Download all app versions available by its package name (e.g. _net.universia.uva_).
    """
    versions = db.get_app_versions_by_package(package)

    if not versions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="App not found"
        )

    return {"app_list": [{"app_hash": h, "version_name": v} for (h, v) in versions]}


@router.post("/post/app/file",
         status_code=status.HTTP_200_OK,
         summary="Upload app by its apk file",
         response_model=Message,
         response_description="Request status (busy, requested)",
         responses={
             400: {
                 "model": Message,
                 "description": "Invalid document type"
             },
         },
         tags=["v2"])
async def post_app_by_file(file: UploadFile) -> dict:
    """Upload app by its apk file.
    """
    response = {"detail": ""}

    if file.content_type != "application/vnd.android.package-archive":
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, 
            detail="Invalid document type"
        )

    file_path = "data/app_uploads/" + file.filename

    try:
        contents = file.file.read()
        with open(file_path, 'wb') as f:
            f.write(contents)
    except Exception:
        response["detail"] = "error"
        return response
    finally:
        file.file.close()

    db.upload_app_by_file(file_path)

    response["detail"] = "requested"

    return response


@router.get("/get/app/name",
         status_code=status.HTTP_200_OK,
         summary="Download app metadata by its name",
         response_model=AppElement,
         response_description="App metadata",
         responses={
             404: {
                 "model": Message,
                 "description": "App not found Error"
             },
         },
         tags=["v2"])
async def get_app_by_name(name: str = Query(description="name of the app to download")) -> dict:
    """Download app metadata by its name (e.g. _Whatsapp_).
    """
    app_data = db.get_app_by_name(name)
    if not app_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="App not found"
        )

    return app_data


@router.get("/get/app/detail/hash",
         status_code=status.HTTP_200_OK,
         summary="Download app metadata by its hash",
         response_model=AppDetailElement,
         response_description="App detail metadata",
         responses={
             404: {
                 "model": Message,
                 "description": "App not found Error"
             },
         },
         tags=["v2"])
async def get_app_by_hash(hash: str = Query(description="hash of the app to download")) -> dict:
    """Download app metadata detail by its hash (e.g. _00006852e356353884f5a4ab213f3739240bb0a526162265f923e2477e2907fd_).
    """
    app_data = db.get_app_by_hash(hash)
    if not app_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="App not found"
        )
    
    app_detail_data = app_data["App"]

    app_detail_data["az_metadata_list"] = db.get_app_detail_by_hash(hash)

    return {"AppDetail": app_detail_data}