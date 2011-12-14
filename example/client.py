
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import shutil

from ConfigParser import RawConfigParser

from src.session import Session

SETTINGS_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'settings.ini')

def main():
    
    config = RawConfigParser()
    config.read(SETTINGS_PATH)
    delete_tempfiles = config.getboolean
    metadata_file_path = config.get('general', 'metadata_temp_file')
    properties_file_path = config.get('general', 'properties_temp_file')
    delete_temp_files = config.getboolean('general', 'delete_temp_files')
    
    with Session.create('1.7.2') as session:
        connected = session.login(
            uri=config.get('urls', 'login'),
            username=config.get('authentication', 'username'),
            password=config.get('authentication', 'password')
        )
        
        if not connected:
            print('Failed to connect')
            sys.exit(1)
        
        print('Client connected')
            
        # GetMetadata
        print('Getting metadata')
        res = session.get_metadata()
        
        with open(metadata_file_path, 'w') as f:
            for line in res:
                f.write(line)
        
        print('Searching properties')
        res = session.search_properties(
            query='(COAGADDPH_f1728=|"1)CSTLSOUTH","10)NORTHCNTY","11)CSTLNORTH","2)METROCNTRL","3)METROUPTWN","4)METRO","5)NRTHCOINLD","6)EASTCNTY","7)INLDEAST","8)INLDSOUTH","9)SOUTHBAY")',
            limit=100
        )
        
        with open(properties_file_path, 'w') as f:
            for line in res:
                f.write(line)
                
        if delete_temp_files:
            if os.path.exists(metadata_file_path):
                os.remove(metadata_file_path)
                
            if os.path.exists(properties_file_path):
                os.remove(properties_file_path)

if __name__ == '__main__':
    main()

