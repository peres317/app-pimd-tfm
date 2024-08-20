from common.domain.element import Element
from common.domain.az_dependency import AzDependency


class AzMetadata(Element):
    """Representation of an AzMetadata.
    """
    
    def __init__(self, 
                 app_hash: str = None,
                 az_metadata_date: str = None,
                 ratings_count: int = None,
                 star_rating: float = None,
                 comment_count: int = None,
                 one_star_ratings: int = None,
                 two_star_ratings: int = None,
                 three_star_ratings: int = None,
                 four_star_ratings: int = None,
                 five_star_ratings: int = None,
                 upload_date: str = None,
                 creator: str = None,
                 developer_name: str = None,
                 developer_address: str = None,
                 developer_email: str = None,
                 developer_website: str = None,
                 size: int = None,
                 num_downloads: str = None,
                 app_url: str = None,
                 app_title: str = None,
                 privacy_policy_url: str = None,
                 az_dependency_list: list[AzDependency] = None,
                 dict: dict = None) -> None:
        """Creates a AzMetadata object.

        Args:
            app_hash (str, optional): Hash of the app. Defaults to None.
            az_metadata_date (str, optional): Date of the metadate. Defaults to 
                None.
            ratings_count (int, optional): Number of ratings. Defaults to None.
            star_rating (float, optional): Mean of rates. Defaults to None.
            one_star_ratings (int, optional): Number of one star ratings. 
                Defaults to None.
            two_star_ratings (int, optional): Number of two star ratings. 
                Defaults to None.
            three_star_ratings (int, optional): Number of three star ratings. 
                Defaults to None.
            four_star_ratings (int, optional): Number of four star ratings. 
                Defaults to None.
            five_star_ratings (int, optional): Number of five star ratings. 
                Defaults to None.
            upload_date (str, optional): Date the app was uploaded to Play 
                Store. Defaults to None.
            creator (str, optional): Name of the creator. Defaults to None.
            developer_name (str, optional): Name of the developer. Defaults to 
                None.
            developer_address (str, optional): Address of the developer. 
                Defaults to None.
            developer_email (str, optional): Email of the developer. Defaults to
                 None.
            developer_website (str, optional): Website of the developer. 
                Defaults to None.
            size (int, optional): Size of the app. Defaults to None.
            num_downloads (str, optional): Number of downloads of the app. 
                Defaults to None.
            app_url (str, optional): Play Store URL of the app. Defaults to None.
            app_title (str, optional): Name of the app. Defaults to None.
            privacy_policy_url (str, optional): Privacy policy URL of the app. 
                Defaults to None.
            az_dependency_list (list[AzDependency], optional): List of 
                dependencies. Defaults to None.
            dict (dict, optional): Dictionary representing the object (discard 
                other params). Defaults to None.
        """
        if dict:
            self.app_hash = dict["app_hash"]
            self.az_metadata_date = dict["az_metadata_date"]
            self.ratings_count = dict["ratings_count"]
            self.star_rating = dict["star_rating"]
            self.comment_count = dict["comment_count"]
            self.one_star_ratings = dict["one_star_ratings"]
            self.two_star_ratings = dict["two_star_ratings"]
            self.three_star_ratings = dict["three_star_ratings"]
            self.four_star_ratings = dict["four_star_ratings"]
            self.five_star_ratings = dict["five_star_ratings"]
            self.upload_date = dict["upload_date"]
            self.creator = dict["creator"]
            self.developer_name = dict["developer_name"]
            self.developer_address = dict["developer_address"]
            self.developer_email = dict["developer_email"]
            self.developer_website = dict["developer_website"]
            self.size = dict["size"]
            self.num_downloads = dict["num_downloads"]
            self.app_url = dict["app_url"]
            self.app_title = dict["app_title"]
            self.privacy_policy_url = dict["privacy_policy_url"]

            az_dependency_list = dict["az_dependency_list"]
            if az_dependency_list:
                az_dependency_list = [AzDependency(dict=d["AzDependency"]) for d in az_dependency_list]
                self.az_dependency_list = az_dependency_list
            else:
                self.az_dependency_list = None
        else:
            self.app_hash = app_hash
            self.az_metadata_date = az_metadata_date
            self.ratings_count = ratings_count
            self.star_rating = star_rating
            self.comment_count = comment_count
            self.one_star_ratings = one_star_ratings
            self.two_star_ratings = two_star_ratings
            self.three_star_ratings = three_star_ratings
            self.four_star_ratings = four_star_ratings
            self.five_star_ratings = five_star_ratings
            self.upload_date = upload_date
            self.creator = creator
            self.developer_name = developer_name
            self.developer_address = developer_address
            self.developer_email = developer_email
            self.developer_website = developer_website
            self.size = size
            self.num_downloads = num_downloads
            self.app_url = app_url
            self.app_title = app_title
            self.privacy_policy_url = privacy_policy_url
            self.az_dependency_list = az_dependency_list
        
    def to_dict(self) -> dict:
        """Creates a dict representing the AzMetadata data.

        Returns:
            dict: Data.
        """
        
        data = {"app_hash": self.app_hash,
                "az_metadata_date": self.az_metadata_date,
                "ratings_count": self.ratings_count,
                "star_rating": self.star_rating,
                "comment_count": self.comment_count,
                "one_star_ratings": self.one_star_ratings,
                "two_star_ratings": self.two_star_ratings,
                "three_star_ratings": self.three_star_ratings,
                "four_star_ratings": self.four_star_ratings,
                "five_star_ratings": self.five_star_ratings,
                "upload_date": self.upload_date,
                "creator": self.creator,
                "developer_name": self.developer_name,
                "developer_address": self.developer_address,
                "developer_email": self.developer_email,
                "developer_website": self.developer_website,
                "size": self.size,
                "num_downloads": self.num_downloads,
                "app_url": self.app_url,
                "app_title": self.app_title,
                "privacy_policy_url": self.privacy_policy_url,
                }
        
        if self.az_dependency_list:
            az_dependency_list = [d.to_dict() for d in self.az_dependency_list]
        else:
            az_dependency_list = None
        data["az_dependency_list"] = az_dependency_list
        
        return {"AzMetadata": data}