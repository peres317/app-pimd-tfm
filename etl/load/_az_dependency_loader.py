from etl.load.mysql_connector import MysqlConnector

from common.domain.az_dependency import AzDependency


class _AzDependencyLoader:
    """Load an AzDependency to warehouse.
    """
    
    def __init__(self) -> None:
        """Creates an AzDependency loader.
        """
        self.mysql_conn = MysqlConnector()
        
    def load_az_dependency(self, az_dependency: AzDependency) -> dict:
        """Loads the AzDependency on database.

        Args:
            az_dependency (AzDependency): AzDependency to load.

        Returns:
            int: Number of rows added (1 if loaded succesfully).
        """
        result = self.download_az_dependency(az_dependency.package, 
                                             az_dependency.version_code)
        if result:
            result = 0
        else:
            result = self.mysql_conn.upload_data(
                "INSERT INTO az_dependency VALUES (%(package)s, %(version_code)s);", 
                {"package": az_dependency.package,
                 "version_code": az_dependency.version_code})
            result = result["row_count"]
                
        return result
    
    def download_az_dependency(self, package: str, version_code: int) -> dict:
        """Downloads a AzDependency from database.

        Args:
            package (str): Id of the AzDependency.
            version_code (int): Id of the AzDependency.

        Returns:
            AzDependency: Object requested.
        """
        result = self.mysql_conn.download_data_by_id(
            "SELECT * FROM az_dependency WHERE " 
            + "package = %(package)s AND version_code = %(version_code)s", 
            {"package": package,
             "version_code": version_code})
        if result:
            return AzDependency(package = result[0],
                                version_code = result[1])
        
        return None