# uas2bufr
Python code to transform Uncrewed Aircraft Systems(UAS) data from netCDF into the WMO BUFR format

# Installation

**Requirements**

- Python 3 and above
- [ecCodes](https://github.com/marijanacrepulja/eccodes)
- WMO BUFR tables version 41

# Running
Convert data from file input_netcdf_filename to BUFR. Write output into output_bufr_filename.  

python3 uas2bufr.py input_netcdf output_bufr_filename

**Example of runnig a python code to convert sample netCDF file in github**  
python3 uas2bufr.py 20230327030016_Lat_46.812245_Lon_6.944007.nc 20230327030016_Lat_46.812245_Lon_6.944007.bufr

# Copyright and license
(C) Copyright 2005- ECMWF.

This software is licensed under the terms of the Apache Licence Version 2.0 which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

In applying this licence, ECMWF does not waive the privileges and immunities granted to it by virtue of its status as an intergovernmental organisation nor does it submit to any jurisdiction.

# Contact
[Marijana Crepulja](https://github.com/marijanacrepulja)

