
import logging
import configparser
import requests
from requests.auth import HTTPBasicAuth
import time
import datetime

RemoniURL = 'https://api.remoni.com/v1/'
RemoniUser = 'ansvp@dongenergy.dk'
RemoniPass = 'Cirkeline1001'

AemsURL = 'http://aems.dk/emoncms/input/post.json?'

def main():


    logging.basicConfig(filename='run.log', level=logging.INFO)
    logging.info('*************Started***************')
    logging.info('')
    logging.info('get_latestHour:')
    get_latestHour()



    logging.info('Finished')


def get_Ids():
    res = requests.get(RemoniURL + 'Units?orderby=UnitId&top=10000',auth=HTTPBasicAuth(RemoniUser,RemoniPass ))
    #res = requests.get(RemoniURL + 'Units?orderby=UnitId&top=10000',auth=HTTPBasicAuth('ansvp@dongenergy.dk', 'Cirkeline1001'))
    #logging.info(res.text)
    logging.info('Return code:')
    logging.info(res.status_code)


def get_latestHour():

    tsUnix = time.time()
    #print(tsUnix)
    tsUnix = tsUnix - 3600
    ts = time.gmtime(tsUnix)
    ts = time.strftime("%Y-%m-%dT%H:%M:%S", ts)
    logging.info('Get Remoni data from:' + str(ts))
    #logging.info(ts)

    res = requests.get(RemoniURL + 'Data?orderby=Timestamp&Timestamp=ge(' + ts +')&UnitId=eq(399)&AggregateType=eq(Minutes5)&top=10000', auth=HTTPBasicAuth(RemoniUser, RemoniPass))
    #res = requests.get('https://api.remoni.com/v1/Data?orderby=Timestamp&Timestamp=ge(2018-01-10T08:00:00)&UnitId=eq(399)&AggregateType=eq(Raw)&top=10000', auth=HTTPBasicAuth(RemoniUser, RemoniPass))
    #https://api.remoni.com/v1/Data?orderby=Timestamp&Timestamp=ge(2018-01-10T08%3A00%3A00.00)&UnitId=eq(399)&AggregateType=eq(Raw)&top=10000

    data = res.json()

    logging.info('Return code:')
    logging.info(res.status_code)
    #logging.info(res.text)
    logging.info('Send data to Aems')
    packageCounter = 0
    for i in data:
        NodeId = str(i['UnitId'])
        UnitName = str(i['DataType'])
        Timestamp = i['Timestamp']
        Value = str(round(i['Value'],2))

        Year =      int(Timestamp[0:4])
        Month =     int(Timestamp[5:7])
        Day =       int(Timestamp[8:10])
        Hour =      int(Timestamp[11:13])
        Minute =    int(Timestamp[14:16])
        Second =    int(Timestamp[17:19])

        NewTimestamp = datetime.datetime(Year,Month,Day,Hour,Minute,Second)
        #print( NewTimestamp)
        unixtime = int(time.mktime(NewTimestamp.timetuple()))
        #print(unixtime)
        #print('1515664800')
        packageCounter += 1
        sendToAems(str(unixtime), NodeId, UnitName, Value)


    logging.info('Packages send to Aems: ' + str(packageCounter))



    #sendToAems('1315575927', '399', 'Test', '0')



#http: // aems.dk / emoncms / input / post.json?time = 1515575927 & node = 1 & csv = 100, 200, 300
#http: // aems.dk / emoncms / input / post.json?node = 1 & json = {power1: 100, power2: 200, power3: 300}

def sendToAems(timeStamp, node, id, value):
    #res = requests.get('http://aems.dk/emoncms/input/post.json?time = 1315575927&node=399&json={external-temperature-1:0,external-temperature-2:0,internal-temperature:0}&apikey=51594d8ec6a8419702dae2f0bee94e97')
    res = requests.get(AemsURL + 'time=' + timeStamp + '&node=' + node + '&json={' + id + ':' + value + '}&apikey=51594d8ec6a8419702dae2f0bee94e97')
    #print(AemsURL + 'time=' + timeStamp + '&node=' + node + '&json={' + id + ':' + value + '}&apikey=51594d8ec6a8419702dae2f0bee94e97')
    #print(value)
    #logging.info('Return code:')
    #logging.info(res.text)
    time.sleep(1)

if __name__ == '__main__':
    main()

