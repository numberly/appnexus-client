class Cursor(object):
    """Represents a cursor on collection of AppNexus objects"""

    batch_size = 100
    common_keys = {"status", "count", "dbg_info", "num_elements",
                   "start_element"}

    def __init__(self, client, service_name, representation, **specs):
        """Initialize the object

        :param client: an AppNexusClient instance
        :param service_name: the service to which the request was made
        :param specs: The specifications sent to AppNexus with the request
        """
        # Health checks
        if client is None or service_name is None:
            raise RuntimeError("client and service can't be set to None")

        if representation is None or not callable(representation):
            raise TypeError("representation must be non-null and callable")

        self.client = client
        self.service_name = service_name
        self.representation = representation
        self.specs = specs
        self._skip = 0
        self._limit = float('inf')

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
        retrieved = 0
        for page in self.iter_pages():
            data = self.extract_data(page)
            for entity in data:
                retrieved += 1
                yield entity

    def extract_data(self, page):
        """Extract the AppNexus object or list of objects from the response"""
        response_keys = set(page.keys())
        uncommon_keys = response_keys - self.common_keys

        for possible_data_key in uncommon_keys:
            element = page[possible_data_key]
            if isinstance(element, dict):
                return [self.representation(self.client, self.service_name,
                                            element)]
            if isinstance(element, list):
                return [self.representation(self.client, self.service_name, x)
                        for x in element]

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
        return self.client.get(self.service_name, **specs)

    def iter_pages(self):
        """Iterate as much as needed to get all available pages"""
        start_element = self._skip
        num_elements = min(self._limit, self.batch_size)
        count = -1
        while start_element < count or count == -1:
            page = self.get_page(start_element, num_elements)
            yield page
            start_element = start_element + page["num_elements"]
            num_elements = min(page["count"] - num_elements, self.batch_size)
            count = min(page["count"], self._skip + self._limit)

    def count(self):
        """Returns the number of elements matching the specifications"""
        return self.get_page(num_elements=1)["count"]

    def clone(self):
        return Cursor(self.client, self.service_name, self.representation,
                      **self.specs)

    def limit(self, number):
        """Limit the cursor to retrieve at most `number` elements"""
        self._limit = number
        return self

    def skip(self, number):
        """Skip the first `number` elements of the cursor"""
        self._skip = number
        return self

    def size(self):
        """Return the number of elements of the cursor with skip and limit"""
        initial_count = self.count()
        count_with_skip = max(0, initial_count - self._skip)
        size = min(count_with_skip, self._limit)
        return size


__all__ = ["Cursor"]
