from requests.auth import AuthBase

class AquariumAuth(AuthBase):
    def __init__(self, token, domain):
        self.token = token
        self.domain = domain

    def __call__(self, r):
        if (self.token):
            r.headers['authorization'] = self.token

        if (self.domain):
            r.headers['aquarium-domain'] = self.domain
        return r