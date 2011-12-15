
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import shutil
import time
from ConfigParser import RawConfigParser
from pprint import pprint
import re

from lxml import etree

from src.session import Session

config = RawConfigParser()
config.read(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'settings.ini'))
delete_tempfiles = config.getboolean
metadata_file_path = config.get('general', 'metadata_temp_file')
properties_file_path = config.get('general', 'properties_temp_file')
delete_temp_files = config.getboolean('general', 'delete_temp_files')
    
def main():
    
    with Session.create('1.7.2') as session:
        connected = session.login(
            uri=config.get('urls', 'login'),
            username=config.get('authentication', 'username'),
            password=config.get('authentication', 'password')
        )
        
        if not connected:
            print('Failed to connect.')
            sys.exit(1)
        
        print('Client connected.')
            
        # GetMetadata
        get_metadata(session)
        
        # Download properties
        download_properties(session)
        
        # Obtain photo URLs
        get_photo_urls(session)
    
    if delete_temp_files:
        if os.path.exists(metadata_file_path):
            os.remove(metadata_file_path)
            
        if os.path.exists(properties_file_path):
            os.remove(properties_file_path)
            
    print('Finished.')

def get_metadata(session):
    print('Getting metadata.')
    res = session.get_metadata()
    
    with open(metadata_file_path, 'w') as f:
        [f.write(line) for line in res]
    print('Done downloading metadata')
    
def download_properties(session):
    print('Searching properties.')
    res = session.search_properties(
        query='(COAGADDPH_f1728=|"1)CSTLSOUTH","10)NORTHCNTY","11)CSTLNORTH","2)METROCNTRL","3)METROUPTWN","4)METRO","5)NRTHCOINLD","6)EASTCNTY","7)INLDEAST","8)INLDSOUTH","9)SOUTHBAY")',
        fields=['sysid', 'MLNumber_f139'],
        format='COMPACT-DECODED',
        limit=10
    )
    print('Got result. Processing...')
    
    start_time = time.time()
    with open(properties_file_path, 'w') as f:
        [f.write(line) for line in res]
    end_time = time.time()
    print('Done downloading properties.')
    print('Finished in {0} seconds.'.format(round(end_time - start_time, 2)))

def get_photo_urls(session):
    i = 0
    sysid_set = []
    for event, elem in etree.iterparse(properties_file_path):
        #print('{0}: {1}, {2}'.format(i, event, elem))
        i = i + 1
        if event == 'end' and elem.tag == 'DATA':
            parts = elem.text.strip().split('\x09')
            sysid_set.append(parts[0])
    
    for sysid in sysid_set:
        
        res = session.get_object(
            type='Photo',
            resource='Property',
            id='{0}:0'.format(sysid),
            # Some servers use the non-standard image/jpg
            accept_types=['image/jpeg'],
            location='1'
        )
        print('Primary Photo: {0}'.format(res.read()))
        
        res = session.get_object(
            type='Photo',
            resource='Property',
            id='{0}:0:*'.format(sysid),
            # Some servers use the non-standard image/jpg
            accept_types=['image/jpeg'],
            location='1'
        )
        
        boundary = None
        info = res.info()
        #print('Content-Type: {0}'.format(info['Content-Type']))
        for i in [i.strip() for i in info['Content-Type'].split(';')]:
            j = i.partition('=')
            if j[0] == 'boundary':
                boundary = j[2]
                
        if boundary:
            #print('Boundary: {0}'.format(boundary))
            expr = re.compile(r"Location:\s(?P<location>[^\r\n]+)", re.MULTILINE)
            encapsulation_boundary = '--{0}'.format(boundary)
            text = res.read()
            #print(text)
            parts = text.split(encapsulation_boundary)
            for i in parts:
                m = expr.search(i)
                if m:
                    print(m.group('location'))
                #else:
                #    print('No match for:\n{0}'.format(i))

if __name__ == '__main__':
    main()
