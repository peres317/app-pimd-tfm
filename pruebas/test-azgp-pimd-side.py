HASH_EXAMPLE = "0000003b455a6c7af837ef90f2eaffd856e3b5cf49f5e27191430328de2fa670"
TSTAMP_EXAMPLE = "2023-04-23 11:15:25"

################
# DOMAIN TESTS #
################
print("Domain Tests")

from common.domain.az_metadata import AzMetadata
from common.domain.az_dependency import AzDependency

dependency = AzDependency("com.example", 0)
r1 = dependency.to_dict()
dependency2 = AzDependency("com.example2", 1)
dependencies = [dependency, dependency2]
dependency_from_dic = AzDependency(dict=dependency.to_dict()["AzDependency"])
r2 = dependency_from_dic.to_dict()
print(r1 == r2)

metadata = AzMetadata(
    app_hash = HASH_EXAMPLE,
    az_metadata_date = TSTAMP_EXAMPLE,
    ratings_count = 1,
    star_rating = 1.0,
    one_star_ratings = 1,
    two_star_ratings = 1,
    three_star_ratings = 1,
    four_star_ratings = 1,
    five_star_ratings = 1,
    upload_date = "date_example",
    creator = "creator_example",
    developer_name = "developername_example",
    developer_address = "developeraddress_example",
    developer_email = "developeremail_example",
    developer_website = "developerwebsite_example",
    size = 1,
    num_downloads = "1 download",
    app_url = "app_url",
    app_title = "title",
    privacy_policy_url = "privacy_policy_url",
    az_dependency_list = dependencies
)
r1 = metadata.to_dict()
metadata2 = AzMetadata(dict=r1["AzMetadata"])
r2 = metadata2.to_dict()
print(r1 == r2)


##############
# LOAD TESTS #
##############
print("Load Tests")
from etl.load._az_dependency_loader import _AzDependencyLoader

l = _AzDependencyLoader()
print(l.download_az_dependency("com.example", 0))
print(l.load_az_dependency(dependency))
print(l.download_az_dependency("com.example", 0).to_dict())

from etl.load.az_metadata_loader import AzMetadataLoader

l = AzMetadataLoader()
print(l.download_az_metadata(HASH_EXAMPLE, TSTAMP_EXAMPLE))
print(l.load_az_metadata(metadata))
print(l.download_az_metadata(HASH_EXAMPLE, TSTAMP_EXAMPLE).to_dict())

#########################
# TODO: run after tests #
#########################
# DELETE FROM az_bind_dependency;
# DELETE FROM az_dependency;
# DELETE FROM az_metadata;