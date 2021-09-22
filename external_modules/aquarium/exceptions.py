class Error(Exception):
    def __init__(self, response):
        url=response.url
        error=response.json().get('error')
        super(Error, self).__init__('{0} - url:{1}'.format(error, url))

#400
class RequestError(Error):
    pass
#401
class AuthentificationError(Error):
    pass
#403
class AutorisationError(Error):
    pass
#404
class PathNotFoundError(Error):
    pass
#409
class ConflictError(Error):
    pass
#413
class UploadExceedLimit(Error):
    pass
#500
class InternalError(Error):
    pass