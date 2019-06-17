from database import get_latest_record
from const import all_instruments

# for checking problem with updating instruments from server
def check_latest_record(list_of_instruments):
    result = dict()
    for instrument in list_of_instruments:
        result[instrument] = get_latest_record(all_instruments.get(instrument))
    return result
