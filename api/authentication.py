from etl.load.mysql_connector import MysqlConnector
from common.util import Util as u

from hashlib import sha256

class Authentication:
    def __init__(self) -> None:
        """Creates a Authentication connection.
        """
        self.mysql_conn = MysqlConnector("MYSQL_CREDENTIALS")
        
    def get_user_name(self, api_key: str) -> str:
        """Get user associated to an api key.

        Args:
            api_key (str): Api key.

        Returns:
            str: Username. None if no user.
        """
        sha256_api_key = sha256(api_key.encode()).hexdigest()
        result = self.mysql_conn.download_all(
            "SELECT user_name FROM credentials WHERE sha256_api_key = %(sha256_api_key)s;",
            {"sha256_api_key": sha256_api_key}
        )
        
        if len(result) == 0:
            return
        
        return result[0][0]
    
    def get_roles(self, api_key: str) -> list[str]:
        """Get the roles for the user provided by its api key.

        Args:
            api_key (str): Api key.

        Returns:
            list[str]: List of roles of the user. None if no user.
        """        
        user_name = self.get_user_name(api_key)
        if not user_name:
            return 
        
        result = self.mysql_conn.download_all(
            "SELECT role_id FROM roles WHERE user_name = %(user_name)s;",
            {"user_name": user_name}
        )
        
        return [role for (role,) in result]
    
    def get_roles_by_user(self, user_name: str) -> list[str]:
        """Get the roles for the user provided.

        Args:
            user_name (str): Username.

        Returns:
            list[str]: List of roles of the user.
        """
        result = self.mysql_conn.download_all(
            "SELECT role_id FROM roles WHERE user_name = %(user_name)s;",
            {"user_name": user_name}
        )
        
        return [role for (role,) in result]
    
    def get_new_valid_api_key(self) -> str: # TODO: lock protect
        """Returns a new valid api key.

        Returns:
            str: New api key.
        """        
        while True:
            api_key = u.get_new_api_key()
            sha256_api_key = sha256(api_key.encode()).hexdigest()
            result = self.mysql_conn.download_all(
                "SELECT sha256_api_key FROM credentials WHERE sha256_api_key = %(sha256_api_key)s;",
                {"sha256_api_key": sha256_api_key}
            )
            if len(result) == 0:
                break
        
        return api_key
    
    def register_user(self, user_name: str) -> str: # TODO: lock protect
        """Register new user by its username.

        Args:
            user_name (str): Username.

        Returns:
            str: Api key for the user. None if username is not valid.
        """        
        if len(user_name) == 0:
            return
        
        result = self.mysql_conn.download_all(
            "SELECT user_name FROM credentials WHERE user_name = %(user_name)s;",
            {"user_name": user_name}
        )
        if len(result) != 0:
            return
        
        api_key = self.get_new_valid_api_key()
        sha256_api_key = sha256(api_key.encode()).hexdigest()
        
        result = self.mysql_conn.upload_data(
            "INSERT INTO credentials VALUES (%(user_name)s, %(sha256_api_key)s);", 
            {"user_name": user_name, "sha256_api_key": sha256_api_key})
        if result["row_count"] != 1:
            return
        
        return api_key
    
    def assign_role(self, user_name: str, role: str) -> bool:
        """Assigns role to username provided.

        Args:
            user_name (str): Username.
            role (str): New role.

        Returns:
            bool: True if role assigned else None.
        """
        result = self.mysql_conn.upload_data(
            "INSERT INTO roles VALUES (%(user_name)s, %(role)s);", 
            {"user_name": user_name, "role": role})
        if result["row_count"] != 1:
            return

        return True
    
    def revoke_access(self, user_name: str) -> bool:
        """Revoke access to api to a user by its username.

        Args:
            user_name (str): Username.

        Returns:
            bool: True if access revoked else None.
        """        
        self.mysql_conn.upload_data(
            "DELETE FROM roles WHERE user_name=%(user_name)s;", 
            {"user_name": user_name})
        result = self.mysql_conn.upload_data(
            "DELETE FROM credentials WHERE user_name=%(user_name)s;", 
            {"user_name": user_name})
        if result["row_count"] != 1:
            return
        
        return True