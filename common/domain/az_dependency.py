from common.domain.element import Element


class AzDependency(Element):
    """Representation of an Androzoo GP dependency.
    """
    
    def __init__(self, 
                 package: str = None, 
                 version_code: int = None,
                 dict: dict = None) -> None:
        """Creates an Androzoo GP dependency.

        Args:
            package (str, optional): Package name of the app. Defaults to None.
            version_code (int, optional): Version code of the app. Defaults to 
                None.
            dict (dict, optional): Dictionary representing the object (discard 
                other params). Defaults to None.
        """
        if dict:
            self.package = dict["package"]
            self.version_code = dict["version_code"]
        else:
            self.package = package
            self.version_code = version_code
        
    def to_dict(self) -> dict:
        """Creates a dict representing the dependency data.

        Returns:
            dict: Data.
        """
        
        data = {"package": self.package,
                "version_code": self.version_code}
        
        return {"AzDependency": data}