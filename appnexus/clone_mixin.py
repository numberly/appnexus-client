clone_services_unrequired_fields = {
    "Advertiser": ["id", "name", "profile_id"],
}


class CloneMixin():

    def clone(self, **kwargs):
        try:
            payload = {}
            for field in self.__dict__.keys():
                if field not in clone_services_unrequired_fields[type(self).__name__]:
                    payload[field] = self.__dict__[field]
            return self.create(payload, **kwargs)
        except KeyError:
            raise NotImplementedError("Clone method isn't yet available for {} service."
                                      .format(self.service_name))


__all__ = ["CloneMixin", "clone_services_unrequired_fields"]
