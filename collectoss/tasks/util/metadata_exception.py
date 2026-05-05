class MetadataException(Exception):
    def __init__(self, original_exception, additional_metadata):
        self.original_exception = original_exception
        self.additional_metadata = additional_metadata
        
        super().__init__(f"{str(self.original_exception)} | Additional metadata: {self.additional_metadata}")
