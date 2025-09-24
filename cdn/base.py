from abc import ABC, abstractmethod

class CDN(ABC):
    def __init__(self, config):
        self.config = config

    @abstractmethod
    def upload_files(self, files_to_upload: list[str], output_dir):
        pass

