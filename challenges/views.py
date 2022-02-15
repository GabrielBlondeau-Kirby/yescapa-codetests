import json
from operator import itemgetter

from django.http import JsonResponse
from django.shortcuts import render
from datetime import datetime


# ==========================================================================================
# LEVEL 1

def v1_search_closer_campers(request):
    """
    GET /v1/search/campers

    :param request: None
    :return: list of searches including the nearest campers
    """
    searches, campers, _ = get_data(1)

    results = dict(results=list())
    for search in searches:
        r_search = dict(search_id=search['id'], search_results=list())
        for camper in campers:
            if _is_camper_in_bounding_box(search, camper):
                r_search['search_results'].append(dict(camper_id=camper['id']))
        results['results'].append(r_search)

    print(json.dumps(results, indent=4))  # Debug
    # return render(request, "search_campers.html", results)
    return JsonResponse(results)


# ==========================================================================================
# LEVEL 2

def v2_search_closer_campers(request):
    """
    GET /v2/search/campers

    :param request: None
    :return: list of searches including the nearest campers
    """
    searches, campers, _ = get_data(2)

    min_day_discount = 7

    results = dict(results=list())
    for search in searches:
        r_search = dict(search_id=search['id'], search_results=list())
        for camper in campers:
            if _is_camper_in_bounding_box(search, camper):
                days = 1 + get_days(search.get('start_date'), search.get('end_date'))
                price = camper['price_per_day'] * days
                if days >= min_day_discount:
                    price -= price * camper.get('weekly_discount', 0)
                r_search['search_results'].append(dict(camper_id=camper['id'], price=price))
        r_search.update({'search_results': sorted(r_search['search_results'], key=itemgetter('price'))})
        results['results'].append(r_search)

    print(json.dumps(results, indent=4))  # Debug

    # return render(request, "search_campers.html", results)
    return JsonResponse(results)


# ==========================================================================================
# LEVEL 3

def v3_search_closer_campers(request):
    """
    GET /v3/search/campers

    :param request: None
    :return: list of searches including the nearest campers
    """
    searches, campers, calendars = get_data(3)

    min_day_discount = 7

    results = dict(results=list())
    for search in searches:
        r_search = dict(search_id=search['id'], search_results=list())
        for camper in campers:
            camper_id = camper['id']

            # Level 3
            if not is_camper_available(camper_id, (search.get('start_date'), search.get('end_date')), calendars):
                continue
            # ==========

            if _is_camper_in_bounding_box(search, camper):
                # weekly_discount
                days = 1 + get_days(search.get('start_date'), search.get('end_date'))
                price = camper['price_per_day'] * days
                if days >= min_day_discount:
                    price -= price * camper.get('weekly_discount', 0)
                r_search['search_results'].append(dict(camper_id=camper_id, price=price))
        r_search.update({'search_results': sorted(r_search['search_results'], key=itemgetter('price'))})

        results['results'].append(r_search)

    print(json.dumps(results, indent=4))  # Debug
    # return render(request, "search_campers.html", results)
    return JsonResponse(results)


def is_camper_available(camper_id: str, date_range: tuple, calendars: list):
    """
    Wil check if the camper is Available or not for the range of date <date_range>.

    :param camper_id: <str> | Id of a camper
    :param date_range: tuple(<str>, <str>) | from Search data
    :param calendars: <list> | list of calendar
    :return: Boolean
    """

    for cal in calendars:
        if camper_id != cal["camper_id"]:
            continue

        if cal.get('camper_is_available', True):
            continue

        if any(d_r is None for d_r in date_range):
            continue

        # Search dates
        start_date = datetime.strptime(date_range[0], "%Y-%m-%d")
        end_date = datetime.strptime(date_range[1], "%Y-%m-%d")

        # Calendar dates
        n_start_date = datetime.strptime(cal['start_date'], "%Y-%m-%d")
        n_end_date = datetime.strptime(cal['end_date'], "%Y-%m-%d")

        if (start_date <= n_start_date <= end_date) or (n_start_date <= start_date <= n_end_date):
            return False
    return True


# ==========================================================================================
# General Methods

def _is_camper_in_bounding_box(s_pos: dict, c_pos: dict, r: float = 0.1):
    """
    Helps to know if the camper is in the Bunding Box of a search.

    :param s_pos: {'latitude': <Float>, 'longitude': <Float> }
    :param c_pos: {'latitude': <Float>, 'longitude': <Float> }
    :param r: The radius of the pos range. __default__ 0.1
    :return: Boolean | True if the camper (c_pos) is in the bunding box else False
    """
    return abs(s_pos['latitude'] - c_pos['latitude']) < r and abs(s_pos['longitude'] - c_pos['longitude']) < r


def get_days(start_date: str, end_date: str):
    """
    Get days between two dates.

    :param start_date: str <HHHH-MM-DD>
    :param end_date: str <HHHH-MM-DD>
    :return: int
    """
    if start_date is None or end_date is None:
        return 0
    return (datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")).days


def get_data(version: int):
    data_path = f'./challenges/data/v{version}/'

    s_file = open(f'{data_path}searches.json')
    searches = json.load(s_file)['searches']

    c_file = open(f'{data_path}campers.json')
    campers = json.load(c_file)['campers']

    try:
        cal_file = open(f'{data_path}calendars.json')
        calendars = json.load(cal_file)['calendars']
    except Exception:
        calendars = None
    return searches, campers, calendars
