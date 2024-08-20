from datetime import datetime
from pydantic import BaseModel
from typing import Union

################
# MISC SCHEMAS #
################

class Message(BaseModel):
    detail: str
    
################
# POST SCHEMAS #
################

class Package(BaseModel):
    package: str
    
class ExpertScore(BaseModel):
    value: float
    app_hash: str

##################
# DOMAIN SCHEMAS #
##################

class Score(BaseModel):
    value: Union[float, None]
    rank_name: str
    app_hash: str
    
class ScoreElement(BaseModel):
    Score: Score

class ExtractionMetadata(BaseModel):
    source: str 
    method: str 
    timestamp: datetime
    
class ExtractionMetadataElement(BaseModel):
    ExtractionMetadata: ExtractionMetadata

class PermissionGroup(BaseModel):
    name: str
    
class PermissionGroupElement(BaseModel):
    PermissionGroup: PermissionGroup
    
class Rank(BaseModel):
    value: float
    rank_name: str
    permission_name: str
    
class RankElement(BaseModel):
    Rank: Rank

class Permission(BaseModel):
    name: str
    protection_level: Union[str, None]
    declared_group_list: Union[list[PermissionGroupElement], None]
    rank_list: Union[list[RankElement], None]
    
class PermissionElement(BaseModel):
    Permission: Permission
    
class App(BaseModel):
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
    
class AppElement(BaseModel):
    App: App