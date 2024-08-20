from datetime import datetime
from pydantic import BaseModel
from typing import Union
from ..models import *

class AppVersion(BaseModel):
    app_hash: str
    version_name: str

class AvailableVersions(BaseModel):
    app_list: list[AppVersion]

class AzDependency(BaseModel):
    package: str
    version_code: int
    
class AzDependencyElement(BaseModel):
    AzDependency: AzDependency

class AzMetadata(BaseModel):
    app_hash: str
    az_metadata_date: datetime
    ratings_count: Union[int, None]
    star_rating: Union[float, None]
    comment_count: Union[int, None]
    one_star_ratings: Union[int, None]
    two_star_ratings: Union[int, None]
    three_star_ratings: Union[int, None]
    four_star_ratings: Union[int, None]
    five_star_ratings: Union[int, None]
    upload_date: Union[str, None]
    creator: Union[str, None]
    developer_name: Union[str, None]
    developer_address: Union[str, None]
    developer_email: Union[str, None]
    developer_website: Union[str, None]
    size: Union[int, None]
    num_downloads: Union[str, None]
    app_url: Union[str, None]
    app_title: Union[str, None]
    privacy_policy_url: Union[str, None]
    az_dependency_list: Union[list[AzDependencyElement], None]
    
class AzMetadataElement(BaseModel):
    AzMetadata: AzMetadata

class AppDetail(BaseModel):
    hash: str
    package: str
    version_code: int 
    version_name: str 
    min_sdk_version: Union[int, None] 
    target_sdk_version: Union[int, None]
    max_sdk_version: Union[int, None]
    category: Union[str, None] 
    uses_permission_list: Union[list[PermissionElement], None]
    defines_permission_list: Union[list[PermissionElement], None]
    defines_group_list: Union[list[PermissionGroupElement], None]
    extraction_metadata_list: Union[list[ExtractionMetadataElement], None]
    score_list: Union[list[ScoreElement], None]
    az_metadata_list: Union[list[AzMetadataElement], None]

class AppDetailElement(BaseModel):
    AppDetail: AppDetail