class Cursor(object):
    """Represents a cursor on collection of AppNexus objects"""

    batch_size = 100
    common_keys = set(["status", "count", "dbg_info", "num_elements",
                       "start_element"])

    def __init__(self, client, service, representation, **specs):
        """Initialize the object

        :param client: an AppNexusClient instance
        :param service: the service to which the request was made
        :param specs: The specifications sent to AppNexus with the request
        """
        # Health checks
        if client is None or service is None:
            raise RuntimeError("client and service can't be set to None")

        if representation is None or not callable(representation):
            raise TypeError("representation must be non-null and callable")

        self.client = client
        self.service = service
        self.representation = representation
        self.specs = specs

    def __len__(self):
        """Returns the number of elements matching the specifications"""
        return self.count()

    def __getitem__(self, idx):
        """Returns the nth element matching the specifications"""
        page = self.get_page(num_elements=1, start_element=idx)
        data = self.extract_data(page)
        return data[0]

    def __iter__(self):
        """Iterate over all AppNexus objects matching the specifications"""
        for page in self.iter_pages():
            data = self.extract_data(page)
            for entity in data:
                yield entity

    def extract_data(self, page):
        """Extract the AppNexus object or list of objects from the response"""
        response_keys = set(page.keys())
        uncommon_keys = response_keys - self.common_keys

        for possible_data_key in uncommon_keys:
            element = page[possible_data_key]
            if isinstance(element, dict):
                return [self.representation(self.client, self.service,
                                            element)]
            if isinstance(element, list):
                return list(map(lambda x: self.representation(self.client,
                                                              self.service, x),
                                element))

    @property
    def first(self):
        """Extract the first AppNexus object present in the response"""
        page = self.get_page(num_elements=1)
        data = self.extract_data(page)
        if data:
            return data[0]

    def get_page(self, start_element=0, num_elements=None):
        """Get a page (100 elements) starting from `start_element`"""
        if num_elements is None:
            num_elements = self.batch_size
        specs = self.specs.copy()
        specs.update(start_element=start_element, num_elements=num_elements)
        return self.client.get(self.service, **specs)

    def iter_pages(self, skip_elements=0):
        start_element = skip_elements
        count = self.count()
        while start_element < count:
            page = self.get_page(start_element)
            yield page
            start_element = page["start_element"] + page["num_elements"]

    def count(self):
        """Returns the number of elements matching the specifications"""
        return self.get_page(num_elements=1)["count"]

    def clone(self):
        return Cursor(self.client, self.service, self.representation,
                      **self.specs)

__all__ = ["Cursor"]
