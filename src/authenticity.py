class AuthenticityCheck:
    def __init__(self):
        self.existing_hashes = set()

    def check_authenticity(self, dataset_hash):
        """Check for duplicate datasets."""
        is_duplicate = dataset_hash in self.existing_hashes
        self.existing_hashes.add(dataset_hash)
        return not is_duplicate