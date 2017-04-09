import requests
import datetime
import pandas as pd
import time

base_url = 'https://script.google.com/macros/s/AKfycbygukdW3tt8sCPcFDlkMnMuNu9bH5fpt7bKV50p2bM/exec?id=1dVz0Og5sZvedwEaQZ_ULjv3gYc-wntjT69NDpY49k4U&sheet=locations.csv'
responseFromServer = requests.get(base_url)
responseInJson = responseFromServer.json()


def requestRespone( url ):
    responseFromServer = requests.get(url)
    responseJson = responseFromServer.json()
    return responseJson;

def MinimumMaximumDateInRange():
    MinimumAndMaximumDateInRange = []
    MinimumAndMaximumDateInRange.append(0)
    MinimumAndMaximumDateInRange.append(0)
    firstIteration = 0
    for loca in responseInJson['locations.csv']:
        if firstIteration == 0:
            MinimumAndMaximumDateInRange[0] = loca.get('date_first')
            MinimumAndMaximumDateInRange[1] = loca.get('date_last')
        if (loca.get('date_first') < MinimumAndMaximumDateInRange[0]):
            MinimumAndMaximumDateInRange[0]  = loca.get('date_first')
        if (loca.get('date_last') < MinimumAndMaximumDateInRange[1]):
            MinimumAndMaximumDateInRange[1] = loca.get('date_last')
        firstIteration = 1
    return MinimumAndMaximumDateInRange

MinimumAndMaximumDateInRange = MinimumMaximumDateInRange()

locationId = []
precipProbability = []
days = []
minDateInAllRanges = 1485907200
maxDateInAllRanges = 1488326400
noOfDays = 0
firstIteration = 0

for loca in responseInJson['locations.csv']:
    url = 'http://api.postcodes.io/postcodes/'
    postalCode = loca.get('postal_code')
    dateFirst = loca.get('date_first')
    dateLast = loca.get('date_last')
    url = url + postalCode
    tempMin = minDateInAllRanges
    tempMax = maxDateInAllRanges
    locationId.append(loca.get('loc_id'))
    cordinatesResponse = requestRespone(url)
    while tempMin <= tempMax:
        if firstIteration is 0:
            date = datetime.datetime.fromtimestamp(int(tempMin)).strftime('%Y-%m-%d')
            days.append(date)

        if (tempMin < dateFirst) or (tempMin > dateLast) or (cordinatesResponse['status'] == 404):
            precipProbability.append('NaN')
        else:
            latitude = cordinatesResponse['result'].get('latitude')
            longitude = cordinatesResponse['result'].get('longitude')
            url = 'https://api.darksky.net/forecast/8b29191b53f16224e5d45f9d91455762/'
            url = url + str(latitude) + ", " + str(longitude) + ", " + str(tempMin) + '?exclude=currently,flags'
            daysPrecipProbabilityResponse = requestRespone(url)
            prepResponse = daysPrecipProbabilityResponse['daily'].get('data')
            if "precipProbability" not in prepResponse[0]:
                precipProbability.append('NaN')
            else:
                precipProbability.append(prepResponse[0]['precipProbability'])
        tempMin = tempMin + 86400
        noOfDays = noOfDays + 1
    firstIteration = 1

numberOfDaysInLargestRange = int(noOfDays/locationId.__len__())
precipProbabilityForEachDay = [precipProbability[x:x+numberOfDaysInLargestRange] for x in range(0, len(precipProbability), numberOfDaysInLargestRange)]

print(days)
print(precipProbabilityForEachDay)
#df = pd.DataFrame(precipProbabilityForEachDay, columns = days, index =  locationId )
#df.index.name = 'Location ID'
#df
