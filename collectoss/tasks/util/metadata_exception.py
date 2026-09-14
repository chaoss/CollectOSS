class MetadataException(Exception):
    def __init__(self, original_exception, additional_metadata):
        self.original_exception = original_exception
        self.additional_metadata = additional_metadata
        
        super().__init__(f"{str(self.original_exception)} | Additional metadata: {self.additional_metadata}")

    def __reduce__(self):
        # billiard pickles task exceptions to send them from the worker child to the
        # parent; the default reduce replays __init__ with the single formatted message
        # and fails on the missing second argument, masking the real failure
        return (self.__class__, (self.original_exception, self.additional_metadata))
