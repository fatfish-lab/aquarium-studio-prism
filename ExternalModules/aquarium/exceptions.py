class Error(Exception):
    def __init__(self, response):
        if (type(response) is str):
            super(Error, self).__init__(response)
        else:
            url=response.url
            status_code=response.status_code
            if status_code == 405:
                error='Method Not Allowed. Use "{0}" instead'.format(
                    response.headers['allowed']
                )
            else:
                try:
                    responseJson = response.json()
                    if ('error' in responseJson):
                        error=responseJson.get('error')
                    else:
                        error = response.text

                except:
                    error=response.text

            super(Error, self).__init__('{0} - url:{1}'.format(error, url))

#400
class RequestError(Error):
    pass
#401
class AuthentificationError(Error):
    pass
class TwoFactorAuthenticationError(Error):
    pass
#403
class AutorisationError(Error):
    pass
#404
class PathNotFoundError(Error):
    pass
#405
class MethodNotAllowed(Error):
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

class Deprecated(Error):
    pass