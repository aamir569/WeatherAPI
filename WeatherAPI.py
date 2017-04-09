import requests
import datetime
import pandas as pd
import time

base_url = 'https://script.google.com/macros/s/AKfycbygukdW3tt8sCPcFDlkMnMuNu9bH5fpt7bKV50p2bM/exec?id=1dVz0Og5sZvedwEaQZ_ULjv3gYc-wntjT69NDpY49k4U&sheet=locations.csv'
responseFromServer = requests.get(base_url)
responseInJson = responseFromServer.json()

# Sends a Get Request and convert Response to JSON
def requestRespone( url ):
    responseFromServer = requests.get(url)
    responseJson = responseFromServer.json()
    return responseJson;

# Finds the date that is minimum in Past ( Minimum Date in Range)
# Finds the date that is maximum in  Past ( Maximum Date in Range)
def MinimumMaximumDateInRange():
    MinimumAndMaximumDateInRange = []
    MinimumAndMaximumDateInRange.append(0)
    MinimumAndMaximumDateInRange.append(0)
    firstIteration = 0
    for location in responseInJson['locations.csv']:
        if firstIteration == 0:
            MinimumAndMaximumDateInRange[0] = location.get('date_first')
            MinimumAndMaximumDateInRange[1] = location.get('date_last')
            firstIteration = 1
        # Finding Maximum Date in Past
        if (location.get('date_first') < MinimumAndMaximumDateInRange[0]):
            MinimumAndMaximumDateInRange[0]  = location.get('date_first')
        # Finding Minimum Date in Past ( nearist to today)
        elif (location.get('date_last') < MinimumAndMaximumDateInRange[1]):
            MinimumAndMaximumDateInRange[1] = location.get('date_last')
    return MinimumAndMaximumDateInRange

# Calling the function to get minimum and maximum dates in past
MinimumAndMaximumDateInRange = MinimumMaximumDateInRange()

# initialization
locationId = []
precipProbability = []
days = []
maximumDateInPast = MinimumAndMaximumDateInRange[0]
minimumDateInPast = MinimumAndMaximumDateInRange[1]
noOfDays = 0
firstIteration = 0


for location in responseInJson['locations.csv']:
    url = 'http://api.postcodes.io/postcodes/'
    postalCode = location.get('postal_code')
    dateFirst = location.get('date_first')
    dateLast = location.get('date_last')
    url = url + postalCode
    maximumDateInPastForInteration = maximumDateInPast
    minimumDateInPastForInteration = minimumDateInPast
    locationId.append(location.get('loc_id'))
    cordinatesResponse = requestRespone(url)
    while maximumDateInPastForInteration <= minimumDateInPastForInteration:
        # Adding all dates in the dates List
        if firstIteration is 0:
            date = datetime.datetime.fromtimestamp(int(maximumDateInPastForInteration)).strftime('%Y-%m-%d')
            days.append(date)
        #  If the date is not the given range or the postal code is not correct
        if (maximumDateInPastForInteration < dateFirst) or (maximumDateInPastForInteration > dateLast) or (cordinatesResponse['status'] == 404):
            precipProbability.append('NaN')
        else:
            latitude = cordinatesResponse['result'].get('latitude')
            longitude = cordinatesResponse['result'].get('longitude')
            url = 'https://api.darksky.net/forecast/8b29191b53f16224e5d45f9d91455762/'
            url = url + str(latitude) + ", " + str(longitude) + ", " + str(maximumDateInPastForInteration) + '?exclude=currently,flags'
            daysPrecipProbabilityResponse = requestRespone(url)
            prepResponse = daysPrecipProbabilityResponse['daily'].get('data')
            if "precipProbability" not in prepResponse[0]:
                precipProbability.append('NaN')
            else:
                precipProbability.append(prepResponse[0]['precipProbability'])

        maximumDateInPastForInteration = maximumDateInPastForInteration + 86400
        print(maximumDateInPastForInteration)
        print(minimumDateInPastForInteration)
        noOfDays = noOfDays + 1
    firstIteration = 1

numberOfDaysInLargestRange = int(noOfDays/locationId.__len__())
precipProbabilityForEachDay = [precipProbability[x:x+numberOfDaysInLargestRange] for x in range(0, len(precipProbability), numberOfDaysInLargestRange)]

df = pd.DataFrame(precipProbabilityForEachDay, columns = days, index =  locationId )
df.index.name = 'Location ID'
df
