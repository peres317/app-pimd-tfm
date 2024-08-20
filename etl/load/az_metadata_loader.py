from etl.load.mysql_connector import MysqlConnector
from etl.load._az_bind_dependency_loader import _AzBindDependencyLoader
from etl.load._az_dependency_loader import _AzDependencyLoader

from common.domain.az_metadata import AzMetadata
from common.domain.az_dependency import AzDependency


class AzMetadataLoader:
    """Load an AzMetadata to warehouse.
    """
    
    def __init__(self) -> None:
        """Creates an AzMetadata loader.
        """
        self.mysql_conn = MysqlConnector()
        
    def load_az_metadata(self, az_metadata: AzMetadata) -> int:
        """Loads app on database.

        Args:
            az_metadata (AzMetadata): AzMetadata to load.

        Returns:
            int: Number of rows added (1 if app loaded succesfully else 0).
        """
        result = self.download_az_metadata(az_metadata.app_hash, 
                                           az_metadata.az_metadata_date)
        if not result:
            result = self.mysql_conn.upload_data("INSERT INTO az_metadata VALUES "
                            + "(%(app_hash)s, %(az_metadata_date)s, %(ratings_count)s, " 
                            + "%(star_rating)s, %(comment_count)s, "
                            + "%(one_star_ratings)s, %(two_star_ratings)s, %(three_star_ratings)s, "
                            + "%(four_star_ratings)s, %(five_star_ratings)s, %(upload_date)s, "
                            + "%(creator)s, %(developer_name)s, %(developer_address)s, "
                            + "%(developer_email)s, %(developer_website)s, %(size)s, "
                            + "%(num_downloads)s, %(app_url)s, %(app_title)s, "
                            + "%(privacy_policy_url)s);", 
                            {"app_hash": az_metadata.app_hash,
                             "az_metadata_date": az_metadata.az_metadata_date,
                             "ratings_count": az_metadata.ratings_count,
                             "star_rating": az_metadata.star_rating,
                             "comment_count": az_metadata.comment_count,
                             "one_star_ratings": az_metadata.one_star_ratings,
                             "two_star_ratings": az_metadata.two_star_ratings,
                             "three_star_ratings": az_metadata.three_star_ratings,
                             "four_star_ratings": az_metadata.four_star_ratings,
                             "five_star_ratings": az_metadata.five_star_ratings,
                             "upload_date": az_metadata.upload_date,
                             "creator": az_metadata.creator,
                             "developer_name": az_metadata.developer_name,
                             "developer_address": az_metadata.developer_address,
                             "developer_email": az_metadata.developer_email,
                             "developer_website": az_metadata.developer_website,
                             "size": az_metadata.size,
                             "num_downloads": az_metadata.num_downloads,
                             "app_url": az_metadata.app_url,
                             "app_title": az_metadata.app_title,
                             "privacy_policy_url": az_metadata.privacy_policy_url})
            result = result["row_count"]
        else:
            result = 0

        # AzDependencies
        if az_metadata.az_dependency_list:
            az_dependency_loader = _AzDependencyLoader()
            b_load = _AzBindDependencyLoader()
            for d in  az_metadata.az_dependency_list:
                p_result = az_dependency_loader.load_az_dependency(d)
                b_load.bind_az_metadata_az_dependency(az_metadata.app_hash,
                                                      az_metadata.az_metadata_date,
                                                      d.package,
                                                      d.version_code)

        return result
    
    def download_az_metadata_list(self, app_hash: str) -> list[AzMetadata]:
        """Downloads a list of all azmetadata for hash on the database.

        Args:
            app_hash (str): hash of app.

        Returns:
            list[(app_hash, az_metadata_date)]:
        """
        result = self.mysql_conn.download_all(
            "SELECT app_hash, az_metadata_date FROM az_metadata "
            + "WHERE app_hash = %(app_hash)s;", {"app_hash": app_hash}
        )
        result_aux = [(hash, date) for (hash, date, ) in result]

        if len(result_aux) > 0:
            result = []
            for (hash, date) in result_aux:
                result.append(self.download_az_metadata(hash, date))
        else:
            result = None 
        
        return result
    
    def download_az_metadata(self, app_hash: str, az_metadata_date: str) -> AzMetadata:
        """Downloads AzMetadata
        
        Args:
            app_hash (str): Hash of app.
            az_metadata_date (str): Date of AzMetadata.

        Returns:
            AzMetadata: Object.
        """
        result = self.mysql_conn.download_data_by_id(
            "SELECT * FROM az_metadata WHERE app_hash = %(app_hash)s AND "
            + "az_metadata_date = %(az_metadata_date)s;",
            {"app_hash": app_hash,
             "az_metadata_date": az_metadata_date}
        )

        if not result:
            return None
        
        print(result)

        # AzDependencies
        dependencies = _AzBindDependencyLoader().download_dependencies(
            result[0], result[1])

        return AzMetadata(
            app_hash = result[0],
            az_metadata_date = result[1],
            ratings_count = result[2],
            star_rating = result[3],
            one_star_ratings = result[4],
            two_star_ratings = result[5],
            three_star_ratings = result[6],
            four_star_ratings = result[7],
            five_star_ratings = result[8],
            upload_date = result[9],
            creator = result[10],
            developer_name = result[11],
            developer_address = result[12],
            developer_email = result[13],
            developer_website = result[14],
            size = result[15],
            num_downloads = result[16],
            app_url = result[17],
            app_title = result[18],
            privacy_policy_url = result[19],
            az_dependency_list = dependencies
        )