
import sys
from os.path import dirname, realpath, join
sys.path.append(dirname(dirname(realpath(__file__))))

from ConfigParser import RawConfigParser

from src.session import Session

SETTINGS_PATH = join(dirname(realpath(__file__)), 'settings.ini')

def main():
    
    config = RawConfigParser()
    config.read(SETTINGS_PATH)
    
    with Session.create('1.7.2') as session:
        connected = session.login(
            uri='http://stagerets01.sandicor.com/Login.asmx/Login',
            username=config.get('authentication', 'username'),
            password=config.get('authentication', 'password')
        )
        if connected:
            print('Client connected')

if __name__ == '__main__':
    main()

