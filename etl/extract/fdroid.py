from selenium.webdriver.common.by import By
from os import listdir, remove
import zipfile

from common.util import Util as u

from etl.extract.live_source import WebSource


class FDroid(WebSource):
    """Represents F-Droid website.
    """
    
    BASE_URL = "https://f-droid.org/en/"
    QUERY_URL = "https://search.f-droid.org/?q={}"
    NAME = "F-Droid"
    
    def __init__(self) -> None:
        """Creates an F-Droid object
        """
        super().__init__()
        self.result = None
        
    def find_app(self, package: str) -> str:
        """Search in website for "package".

        Args:
            package (str): Package to find.

        Returns:
            str: Package found. None if not found.
        """
        u.log_normal("Finding app " + package + " on F-Droid website...")
        
        result = self._find_app_by_name(package)
        if not result:
            self.driver.close()
            u.log_warning("Empty list.", "No package " + package + " found on "
                          + "F-Droid website.")
            return None
        
        self.result = result
        package, url = result
        
        u.log_result("Found " + package + " package on F-Droid.")
        
        return package
    
    def download_app(self, package: str) -> str:
        """Download app by package. Package must exist on website.

        Args:
            package (str): Package found on website.

        Returns:
            str: File directory
        """
        u.log_normal("Downloading app " + package + " from F-Droid website...")
        
        # Get app page
        if self.result:
            package, url = self.result
        else:
            package, url = self._find_app_by_name(package)
        super()._load_content_page(url)
        
        # Extract download link    
        link_elements = self.driver.find_elements(By.TAG_NAME, "a")
        download_links = [e.get_attribute("href") for e in link_elements]
        download_links = [l for l in download_links if l]
        download_links = [l for l in download_links if l.split(".")[-1] == "apk"][1:]

        if len(download_links) == 0:
            self.driver.close()
            u.log_error("File not found.", "Downloading error.")
            return None
    
        # Download app
        filename = super()._download_file_page(download_links[0])
        if not filename:
            self.driver.close()
            u.log_error("File not found.", "Downloading %s error." 
                        % download_links[0])
            return None
        apk_filename = filename
        
        u.log_result(FDroid.DOWNLOAD_DIR_REL + apk_filename + " downloaded.")
        
        return FDroid.DOWNLOAD_DIR_REL + apk_filename
    
    def _find_app_by_name(self, name: str) -> tuple[str, str]:
        """Finds app by package.

        Args:
            package (str): App package.

        Returns:
            tuple[str, str]: (package, app_url). None if not found.
        """
        # Load website
        url = FDroid.QUERY_URL.format(name)
        super()._load_content_page(url)
        
        # Return first download result of query
        link_elements = self.driver.find_elements(By.TAG_NAME, "a")
        link_list = [elem.get_attribute("href") for elem in link_elements]
        link_list = [link for link in link_list if link]
        link_list = [link for link in link_list if "packages" in link]

        if len(link_list) > 0:
            return (link_list[0].split("/")[-1], link_list[0])

        return None
