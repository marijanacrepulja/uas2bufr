# Copyright 2005- ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
#
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

# Description: How to encode UAS netCDF dataset into BUFR

from __future__ import print_function
import datetime
import traceback
import numpy as np
import sys
import collections
import time
import calendar
from datetime import datetime, timedelta, date
import math
#from datetime import date, timedelta
from netCDF4 import Dataset
from eccodes import *
np.set_printoptions(threshold=np.inf)


VERBOSE = 1  # verbose error reporting

def rangeValues(scale, reference, width):

    valueMax= (pow(2,width) -2 + reference)*(pow(10,-scale))
    valueMin= reference * (pow(10,-scale))

    return valueMax, valueMin 

def read_netcdf(nc_filename):

    uas2Dict={}

    uas = Dataset(nc_filename, 'r')

    platform_name= uas.getncattr('platform_name')
    uas2Dict['platform_name']=platform_name.replace("-", "")
    uas2Dict['numSubsets']=uas.dimensions['obs'].size
    uas2Dict['time']=uas.variables['time'][:]
    uas2Dict['lon']=uas.variables['lon'][:]
    uas2Dict['lat']=uas.variables['lat'][:]
    uas2Dict['temp']=uas.variables['temp'][:]
    uas2Dict['rel_hum']=uas.variables['rel_hum'][:]
    uas2Dict['mixing_ratio']=uas.variables['mixing_ratio'][:]
    uas2Dict['air_press']=uas.variables['air_press'][:]
    uas2Dict['wind_speed']=uas.variables['wind_speed'][:]
    uas2Dict['wind_dir']=uas.variables['wind_dir'][:]


    ## The product time is in units
    units_time=getattr(uas.variables['time'], 'units')
    mytime = units_time.split(" ")
    mytime1= (mytime[2].split('-'))
    syear=mytime1[0]
    smonth=mytime1[1]
    mytime2=mytime1[2].split(':')
    sday=mytime2[0][:2]
    shour=mytime2[0][3:5]
    smin=mytime2[1]
    ssec=mytime2[2][:2]

    uas2Dict['syear']=int(syear)
    uas2Dict['smonth']=int(smonth)
    uas2Dict['sday']=int(sday)
    uas2Dict['shour']=int(shour)
    uas2Dict['smin']=int(smin)
    uas2Dict['ssec']=int(ssec)

    uas.close()
    return uas2Dict


def uas2bufr(nc_filename,output_filename):

    uas2Dict_read=read_netcdf(nc_filename)



    dates =[  datetime(uas2Dict_read['syear'],
                       uas2Dict_read['smonth'],
                       uas2Dict_read['sday'],
                       uas2Dict_read['shour'],
                       uas2Dict_read['smin'],
                       uas2Dict_read['ssec'])+timedelta(seconds=float(s)) for s in uas2Dict_read['time']]


    year=[ d.year  for d in dates]
    month=[ d.month  for d in dates]
    day=[ d.day  for d in dates]
    hour=[ d.hour  for d in dates]
    minute=[ d.minute  for d in dates]
    #second=[ (d.second+ d.microsecond/1.0e6)  for d in dates]
    second=[ d.second for d in dates]

 
 #encoding into BUFR
    fbufrout = open(output_filename, 'wb')

    ibufr=codes_bufr_new_from_samples('BUFR4')


    codes_set(ibufr, 'masterTableNumber', 0)
    codes_set(ibufr, 'bufrHeaderSubCentre', 0)
    codes_set(ibufr, 'bufrHeaderCentre', 98)
    codes_set(ibufr, 'updateSequenceNumber', 0)
    codes_set(ibufr, 'dataCategory', 2)
    codes_set(ibufr, 'internationalDataSubCategory', 255)
    codes_set(ibufr, 'masterTablesVersionNumber', 40)
    #codes_set(ibufr, 'masterTablesVersionNumber', 41)
    codes_set(ibufr, 'localTablesVersionNumber', 0)
    codes_set(ibufr, 'typicalYear',int(year[0]))
    codes_set(ibufr, 'typicalMonth',int(month[0]))
    codes_set(ibufr, 'typicalDay',int(day[0]))
    codes_set(ibufr, 'typicalHour',int(hour[0]))
    codes_set(ibufr, 'typicalMinute',int(minute[0]))
    codes_set(ibufr, 'typicalSecond',int(second[0]))
 
    codes_set(ibufr, 'observedData', 1)

    codes_set(ibufr, 'numberOfSubsets', uas2Dict_read['numSubsets'])

    codes_set(ibufr, 'compressedData', 1)

    unexpandedDescriptors =[301150,1008,1095,301011,301013,301021,1013,8009,7010,33003,11001,11002,12101,2170,201135,202130,13003,202000,201000,201144,202133,13002,202000,201000,11073,11075]

    codes_set_array(ibufr, 'unexpandedDescriptors', unexpandedDescriptors)

    #unexpandedDescriptors =311013
    #codes_set(ibufr, 'unexpandedDescriptors', unexpandedDescriptors)



    codes_set(ibufr, 'wigosIdentifierSeries', CODES_MISSING_LONG)
    codes_set(ibufr, 'wigosIssuerOfIdentifier', CODES_MISSING_LONG)
    codes_set(ibufr, 'wigosIssueNumber', CODES_MISSING_LONG)
    codes_set(ibufr, 'wigosLocalIdentifierCharacter','')
    codes_set(ibufr, 'aircraftRegistrationNumberOrOtherIdentification',uas2Dict_read['platform_name'])
    codes_set(ibufr, 'observerIdentification','')

    codes_set_array(ibufr, 'year', year)
    codes_set_array(ibufr, 'month', month)
    codes_set_array(ibufr, 'day', day)
    codes_set_array(ibufr, 'hour', hour)
    codes_set_array(ibufr, 'minute', minute)
    codes_set_array(ibufr, 'second',second)
    codes_set_array(ibufr, 'longitude', uas2Dict_read['lon'][:])
    codes_set_array(ibufr, 'latitude', uas2Dict_read['lat'][:])

    codes_set(ibufr, 'movingObservingPlatformSpeed', CODES_MISSING_LONG)
    codes_set(ibufr, 'detailedPhaseOfFlight', CODES_MISSING_LONG)
    codes_set(ibufr, 'flightLevel', CODES_MISSING_LONG)
    codes_set(ibufr, 'qualityInformation', CODES_MISSING_LONG)
    codes_set_array(ibufr, 'windDirection', uas2Dict_read['wind_dir'][:])
    codes_set_array(ibufr, 'windSpeed', uas2Dict_read['wind_speed'][:])
    codes_set_array(ibufr, 'airTemperature', uas2Dict_read['temp'][:])
    codes_set(ibufr, 'aircraftHumiditySensors', CODES_MISSING_LONG)
    codes_set_array(ibufr, 'relativeHumidity', 100*uas2Dict_read['rel_hum'][:])
    codes_set_array(ibufr, 'mixingRatio', uas2Dict_read['mixing_ratio'][:])
    codes_set(ibufr, 'turbulentKineticEnergy', CODES_MISSING_DOUBLE)
    codes_set(ibufr, 'meanTurbulenceIntensityEddyDissipationRate', CODES_MISSING_DOUBLE)

    codes_set(ibufr, 'pack', 1)
    codes_write(ibufr, fbufrout)

    codes_release(ibufr)
    fbufrout.close()

def main():
    if len(sys.argv) < 3:
        print('Usage: ', sys.argv[0], ' netCDF_input_filename BUFR_output_filename', file=sys.stderr)
        sys.exit(1)
 
    nc_filename = sys.argv[1]
    output_filename = sys.argv[2]


    try:
        uas2bufr(nc_filename,output_filename)

    except ValueError as ve :
        traceback.print_exc(file=sys.stdout)
        logging.error(ve.message) 
    except Exception as e:
        traceback.print_exc(file=sys.stdout)

        return 1

if __name__ == "__main__":
    sys.exit(main())

