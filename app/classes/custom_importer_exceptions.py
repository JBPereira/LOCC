class DataNotUpdatedException(Exception):

    def __init__(self, message):

        super(DataNotUpdatedException, self).__init__(message)


class NoDataDownloadedException(Exception):
    def __init__(self):
        message = 'No data downloaded yet'
        super(NoDataDownloadedException, self).__init__(message)