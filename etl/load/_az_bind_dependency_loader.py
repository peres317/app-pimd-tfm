from etl.load.mysql_connector import MysqlConnector

from common.domain.az_dependency import AzDependency


class _AzBindDependencyLoader:
    """Binds an az_metadata with one or more az_dependency.
    """
    
    def __init__(self) -> None:
        """Creates the loader.
        """
        self.mysql_conn = MysqlConnector()
        
    def bind_az_metadata_az_dependency(self, app_hash: str, 
                                       az_metadata_date: str, 
                                       package: str,
                                       version_code: int) -> int:
        """Loads the bind on database.

        Args:
            app_hash (str): Hash of AzMetadata.
            az_metadata_date (str): Timestamp of AzMetadata.
            package (str): Package of dependency.
            version_code (int): Version code of dependency.

        Returns:
            int: Number of rows added (1 if app loaded succesfully).
        """
        result = self.mysql_conn.upload_data(
            "INSERT INTO az_bind_dependency VALUES "
            + "(%(app_hash)s, %(az_metadata_date)s, "
            + "%(package)s, %(version_code)s);", 
            {"app_hash": app_hash,
             "az_metadata_date": az_metadata_date,
             "package": package,
             "version_code": version_code})
                
        return result["row_count"]
    
    def download_dependencies(self, app_hash: str, 
                              az_metadata_date: str) -> list[AzDependency]:
        """Downloads all the dependencies binded to azMetadata.

        Args:
            app_hash (str): App hash.
            az_metadata_date (str): AzMetadata date.

        Returns:
            list[AzDependency]: AzDependencies.
        """
        result = self.mysql_conn.download_all(
            "SELECT az_dependency_package, az_dependency_version_code " 
            + "FROM az_bind_dependency " 
            + "WHERE az_metadata_app_hash = %(app_hash)s AND " 
            + "az_metadata_az_metadata_date = %(az_metadata_date)s;",
            {"app_hash": app_hash,
             "az_metadata_date": az_metadata_date}
        )
        
        dependencies = [AzDependency(d[0], d[1]) for d in result]
        
        return dependencies