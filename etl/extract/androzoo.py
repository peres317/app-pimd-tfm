from typing import Iterator
from pyandrozoo import pyAndroZoo
import gzip
from alive_progress import alive_bar
from random import random
import json
import requests as r

from common.util import Util as u

from common.domain.az_metadata import AzMetadata
from common.domain.az_dependency import AzDependency


class Androzoo:
    """Represents Androzoo source.
    """
    
    CONFIG_FILE = "data/config.json"
    NUM_APPS = 22086095
    NAME = "Androzoo"
    
    def __init__(self) -> None:
        """Creates a Androzoo object.
        """
        self.API_KEY = None
        self.INDEX_FILE = None
        try:
            with open(Androzoo.CONFIG_FILE, '+r', encoding="utf8") as config:
                azoo_data = json.loads(config.read())["ANDROZOO"]
                self.API_KEY = azoo_data["API_KEY"]
                self.INDEX_FILE = azoo_data["INDEX_FILE"]
        except:
            pass
        
        if not self.API_KEY:
            u.log_error("File not found.", "Androzoo api key not found.")
            
    def get_name(self) -> str:
        """Return the name of the source.

        Returns:
            str: Source name.
        """
        return Androzoo.NAME
            
    def download_apps(self, app_hash_list: list[str]) -> None:
        """Download apps contained in app_hash_list 20 by 20.

        Args:
            app_hash_list (list[str]): List of app hashes.
        """
        u.log_normal("Downloading %d apps..." % len(app_hash_list))
        
        # TODO: call with no app_hash from database (prevent duplication)
        androzoo = pyAndroZoo(self.API_KEY)
        
        # Prepare to download apps 20 by 20
        lists = []
        last_i = 0
        for i in range(len(app_hash_list) // 20):
            lists.append(app_hash_list[(5*i):((5*i+20))])
            last_i = i
        lists.append(app_hash_list[(5*last_i):])
        
        # Download apps
        with alive_bar(len(lists)) as bar:
            for i in self._get_apks(androzoo, lists):
                bar()
        
        u.log_result("Downloaded %d apps." % len(app_hash_list))
        
    def _get_apks(self, androzoo: pyAndroZoo, lists: list[list[str]]) -> None:
        """Download all apps contained in lists from androzoo.

        Args:
            androzoo (pyAndroZoo): Androzoo client.
            lists (list[list[str]]): List of lists of app hashes.
        """
        for list in lists:
            androzoo.get(list) # TODO: pyAndroZoo modded to download in data and timeout added
            yield
        
    def get_n_random_hash(self, n_hash: int) -> list[str]:
        """Select n_hash random from index file.

        Args:
            n_hash (int): Number of apps to select. Function will select n_apps
                or less but a close number.

        Returns:
            list[str]: List of hashes.
        """
        u.log_normal("Finding %d random app hashes..." % n_hash)
        
        # Prevent from not selecting any app when small amount
        n_apps = n_hash
        if n_hash < 10:
            n_apps = 10
        
        selected_hash_list = []
        with alive_bar(n_hash) as bar:
            c = 0
            for i in self._select_random_apps(n_apps):
                c += 1
                selected_hash_list.append(i)
                
                bar()
                
                # Prevent from selecting more than should
                if c >= n_hash:
                    break
                
        u.log_result("%d app hashes found." % len(selected_hash_list))
        
        return selected_hash_list
    
    def get_n_random_hash_by_package(self, n_hash: int,
                                     package_list: list[str]) -> list[str]:
        """Select n_hash random from index file.

        Args:
            n_hash (int): Number of apps to select. Function will select n_apps
                or less but a close number.
            package_list (list[str]): Packages allowed to be downloaded.

        Returns:
            list[str]: List of hashes.
        """
        u.log_normal("Finding %d app hashes by package..." % n_hash)
        
        selected_hash_list = []
        with alive_bar(n_hash) as bar:
            c = 0
            for i in self._select_random_apps_by_package(n_hash, package_list):
                c += 1
                selected_hash_list.append(i)
                
                bar()
                
                # Prevent from selecting more than should
                if c >= n_hash:
                    break
                
        u.log_result("%d app hashes found by package." 
                     % len(selected_hash_list))
        
        return selected_hash_list
    
    def _select_random_apps(self, n_apps: int) -> str:
        """Select n_app random app hashes from index file.

        Args:
            n_apps (int): Number of apps to select. Function will select n_apps
                or less but a close number.

        Returns:
            str: Hash of app selected.

        Yields:
            Iterator[str]: Hash of app selected.
        """
        # Probability of select an app
        p_select = n_apps / Androzoo.NUM_APPS
        
        with gzip.open(self.INDEX_FILE, 'r') as index:
            apps_selected = 0
            header = True
            for app in index:
                # Skip header line
                if header:
                    header = False
                    continue
                
                # Select app
                if random() < p_select:
                    apps_selected += 1
                    yield app.decode("utf-8").split(",")[0]

                    if apps_selected >= n_apps:
                        break
                    
    def _select_random_apps_by_package(self, n_apps: int, 
                                       package_list: list[str]) -> str:
        """Select n_app random app hashes from index file. Apps package must be
        inside package_list. It could select less than n_app.

        Args:
            n_apps (int): Number of apps to select. Function will select n_apps
                or less but a close number.
            package_list (list[str]): Packages allowed to be downloaded.

        Returns:
            str: Hash of app selected.

        Yields:
            Iterator[str]: Hash of app selected.
        """
        with gzip.open(self.INDEX_FILE, 'r') as index:
            apps_selected = 0
            header = True
            for app in index:
                # Skip header line
                if header:
                    header = False
                    continue
                
                # Select app
                file_row = app.decode("utf-8").split(",")
                if file_row[5][1:-1] in package_list:
                    apps_selected += 1
                    yield file_row[0]

                    if apps_selected >= n_apps:
                        break


class AndrozooGP:
    """Represents Androzoo source.
    """

    QUERY_URL = "https://androzoo.uni.lu/api/get_gp_metadata/{package}/{version_code}"

    def __init__(self) -> None:
        """Creates a AndrozooGP object.
        """
        self.API_KEY = None
        try:
            with open(Androzoo.CONFIG_FILE, '+r', encoding="utf8") as config:
                azoo_data = json.loads(config.read())["ANDROZOO"]
                self.API_KEY = azoo_data["API_KEY"]
        except:
            pass
        
        if not self.API_KEY:
            u.log_error("File not found.", "Androzoo api key not found.")


    def get_az_metadata(self, package: str, version_code: str, app_hash: str) -> list[AzMetadata]:
        """Downloads all AzMetadata available on AndrozooGP for an app.

        Args:
            package (str): Package name of the app.
            version_code (str): Version code of the app.
            app_hash (str): Hash of the app

        Returns:
            list[AzMetadata]: List of AzMetadata objects or None.
        """
        url = AndrozooGP.QUERY_URL.format(package=package, version_code=version_code)

        api_response = r.get(url, {"apikey": self.API_KEY})

        response_list = json.loads(api_response.content.decode("utf-8")[:-1])

        az_metadata_list = []
        if len(response_list) > 0:
            for az_metadata_raw in response_list:
                az_metadata_list.append(self._parse_json(az_metadata_raw, app_hash))

        if len(az_metadata_list) == 0:
            az_metadata_list = None

        return az_metadata_list

    def _parse_json(self, az_metadata_raw: dict, app_hash: str, log: bool = False) -> AzMetadata:
        # Convert into AzMetadata object
        dependencies = []
        try:
            l = az_metadata_raw["details"]["appDetails"]["dependencies"]["dependency"]
            for dependency in l:
                dependencies.append(
                    AzDependency(dependency["packageName"], 
                                 dependency["version"])
                )
        except Exception:
            if log:
                u.log_warning("Metadata", "No dependencies were found.")

        az_metadata_date = None
        try:
            az_metadata_date = az_metadata_raw["az_metadata_date"]
        except Exception:
            if log:
                u.log_warning("Metadata", "No az_metadata_date were found.")

        ratings_count = None
        try:
            ratings_count = int(az_metadata_raw["aggregateRating"]["ratingsCount"])
        except Exception:
            if log:
                u.log_warning("Metadata", "No ratings_count were found.")

        star_rating = None
        try:
            star_rating = int(az_metadata_raw["aggregateRating"]["starRating"])
        except Exception:
            if log:
                u.log_warning("Metadata", "No star_rating were found.")

        one_star_ratings = None
        try:
            one_star_ratings = int(az_metadata_raw["aggregateRating"]["oneStarRatings"])
        except Exception:
            if log:
                u.log_warning("Metadata", "No one_star_ratings were found.")

        two_star_ratings = None
        try:
            two_star_ratings = int(az_metadata_raw["aggregateRating"]["twoStarRatings"])
        except Exception:
            if log:
                u.log_warning("Metadata", "No two_star_ratings were found.")

        three_star_ratings = None
        try:
            three_star_ratings = int(az_metadata_raw["aggregateRating"]["threeStarRatings"])
        except Exception:
            if log:
                u.log_warning("Metadata", "No three_star_ratings were found.")

        four_star_ratings = None
        try:
            four_star_ratings = int(az_metadata_raw["aggregateRating"]["fourStarRatings"])
        except Exception:
            if log:
                u.log_warning("Metadata", "No four_star_ratings were found.")

        five_star_ratings = None
        try:
            five_star_ratings = int(az_metadata_raw["aggregateRating"]["fiveStarRatings"])
        except Exception:
            if log:
                u.log_warning("Metadata", "No five_star_ratings were found.")

        upload_date = None
        try:
            upload_date = az_metadata_raw["details"]["appDetails"]["uploadDate"]
        except Exception:
            if log:
                u.log_warning("Metadata", "No upload_date were found.")

        creator = None
        try:
            creator = az_metadata_raw["creator"]
        except Exception:
            if log:
                u.log_warning("Metadata", "No creator were found.")

        developer_name = None
        try:
            developer_name = az_metadata_raw["details"]["appDetails"]["developerName"]
        except Exception:
            if log:
                u.log_warning("Metadata", "No developer_name were found.")

        developer_address = None
        try:
            developer_address = az_metadata_raw["details"]["appDetails"]["developerAddress"]
        except Exception:
            if log:
                u.log_warning("Metadata", "No developer_address were found.")
                        
        developer_email = None
        try:
            developer_email = az_metadata_raw["details"]["appDetails"]["developerEmail"]
        except Exception:
            if log:
                u.log_warning("Metadata", "No developer_email were found.")

        developer_website = None
        try:
            developer_website = az_metadata_raw["details"]["appDetails"]["developerWebsite"]
        except Exception:
            if log:
                u.log_warning("Metadata", "No developer_website were found.")

        size = None
        try:
            size = int(az_metadata_raw["details"]["appDetails"]["installationSize"])
        except Exception:
            if log:
                u.log_warning("Metadata", "No size were found.")

        num_downloads = None
        try:
            num_downloads = az_metadata_raw["details"]["appDetails"]["numDownloads"]
        except Exception:
            if log:
                u.log_warning("Metadata", "No num_downloads were found.")

        app_url = None
        try:
            app_url = az_metadata_raw["shareUrl"]
        except Exception:
            if log:
                u.log_warning("Metadata", "No app_url were found.")

        app_title = None
        try:
            app_title = az_metadata_raw["title"]
        except Exception:
            if log:
                u.log_warning("Metadata", "No app_title were found.")
                        
        privacy_policy_url = None
        try:
            privacy_policy_url = az_metadata_raw["relatedLinks"]["privacyPolicyUrl"]
        except Exception:
            if log:
                u.log_warning("Metadata", "No privacy_policy_url were found.")

        return AzMetadata(
            app_hash = app_hash,
            az_metadata_date = az_metadata_date,
            ratings_count = ratings_count,
            star_rating = star_rating,
            one_star_ratings = one_star_ratings,
            two_star_ratings = two_star_ratings,
            three_star_ratings = three_star_ratings,
            four_star_ratings = four_star_ratings,
            five_star_ratings = five_star_ratings,
            upload_date = upload_date,
            creator = creator,
            developer_name = developer_name,
            developer_address = developer_address,
            developer_email = developer_email,
            developer_website = developer_website,
            size = size,
            num_downloads = num_downloads,
            app_url = app_url,
            app_title = app_title,
            privacy_policy_url = privacy_policy_url,
            az_dependency_list = dependencies
        )

    def bulk_load_from_index(self, index: str, l: int, app_list: dict, log=False) -> list[AzMetadata]:
        """Extract all AzMetadata valid objects.

        Args:
            index (str): Path of the index file.
            app_list (dict): Apps in warehouse {"package_name": [(version_code1, list[hash]), ...]}
            l (int): Number of records in index.

        Returns:
            list[AzMetadata]: List of all AzMetadata that can be uploaded.
        """
        u.log_normal("Finding AzMetadata in index...")
        
        metadata_list = []
        with alive_bar(l) as bar:
            c = 0
            for i in self._bulk_load_from_index(index, app_list):
                if i:
                    az_metadata_raw, hash_list = i

                    for app_hash in hash_list:
                        metadata = self._parse_json(
                            az_metadata_raw, app_hash
                        )
                        c += 1
                        metadata_list.append(metadata)

                bar()
                
        u.log_result("%d AzMetadata found." % len(metadata_list))
        
        return metadata_list

    def _bulk_load_from_index(self, index: str, app_list: dict) -> Iterator[dict]:
        """Returns az_metadata raw json for app in warehouse.

        Args:
            index (str): Path of the index file.
            app_list (dict): Apps in warehouse {"package_name": [(version_code1, list[hash]), ...]}

        Yields:
            Iterator[tuple(dict, hash_list)]: Dict with the az_metadata raw.
        """
        with gzip.open(index, 'r') as i:
            for metadata in i:
                app_metadata = json.loads(metadata)

                r = None

                # App in warehouse?
                try:
                    if app_metadata["docid"] in app_list.keys():
                        hash_list = []

                        for (vc, hl) in app_list[app_metadata["docid"]]:
                            if app_metadata["details"]["appDetails"]["versionCode"] == vc:
                                hash_list += hl
                        
                        if len(hash_list) != 0:
                            r = (app_metadata, hash_list)
                except Exception:
                    u.log_error("Parse", "Could not parse index line.")

                yield r