import datetime as dt


def year(request):
    result = dt.datetime.now().year
    return {'year': result}
