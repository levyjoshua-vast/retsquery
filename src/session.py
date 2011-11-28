
from pprint import pprint
import urllib
import urllib2
import re
import hashlib
import time
import cookielib
import urlparse
from lxml import etree

from exceptions import RETSQueryException
import utilities
import patchedurllib2

RETSQUERY_VERSION = '0.0.1'

class Session(object):
    
    def __init__(self, impl):
        self.__impl = impl
    
    @classmethod
    def create(cls, version=None, implementation=None):
        if not implementation is None:
            return Session(implementation)
            
        map = {
            '1.7.2': SessionImpl_1_7_2
        }
            
        try:
            return Session(map[version]())
        except KeyError:
            raise RETSQueryException("""'{0}' is an invalid or unsupported RETS \
version number.\nValid versions: {1}""".format(version, ','.join(map.iterkeys())))

    def login(self, uri, username, password):
        return self.__impl.login(uri, username, password)
        
    def logout(self):
        if self.__impl.is_logged_in:
            self.__impl.logout()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logout()
    
    def __enter__(self):
        return self
    
class SessionImpl_1_7_2(object):
        
    def __init__(self):
        
        self.__is_logged_in = False
        self.__cookie_jar = cookielib.CookieJar()
        self.__base_url = None
        
        self.__broker_code = None
        self.__broker_branch = None
        self.__member_name = None
        self.__min_metadata_version = None
        self.__metadata_version = None
        self.__metadata_ts = None
        self.__user_id = None
        self.__user_level = None
        self.__user_class = None
        self.__agent_code = None
        self.__timeout_seconds = None
        
        # URLs
        self.__action = None
        self.__change_password = None
        self.__get_object = None
        self.__login = None
        self.__login_complete = None
        self.__logout = None
        self.__search = None
        self.__get_metadata = None
        self.__server_information = None
        self.__update = None
    
    @property
    def is_logged_in(self):
        return self.__is_logged_in
    
    @property
    def base_url(self):
        return self.__base_url
    
    @base_url.setter
    def base_url(self, value):
        self.__base_url = value
    
    @property
    def action_url(self):
        return self.__action
        
    @property
    def change_password_url(self):
        return self.__change_password
    
    @property
    def get_object_url(self):
        return self.__get_object
    
    @property
    def login_url(self):
        return self.__login
    
    @property
    def login_complete_url(self):
        return self.__login_complete
    
    @property
    def logout_url(self):
        return self.__logout
    
    @property
    def search_url(self):
        return self.__search
    
    @property
    def get_metadata_url(self):
        return self.__get_metadata
    
    @property
    def server_information_url(self):
        return self.__server_information
    
    @property
    def update_url(self):
        return self.__update
        
    @property
    def timeout_seconds(self):
        return self.__timeout_seconds
        
    @property
    def user_id(self):
        return self.__user_id
    
    @property
    def user_level(self):
        return self.__user_level
    
    @property
    def user_class(self):
        return self.__user_class
    
    @property
    def agent_code(self):
        return self.__agent_code
        
    @property
    def metadata_timestamp(self):
        return self.__metadata_ts
    
    @property
    def min_metadata_version(self):
        return self.__min_metadata_version
    
    @property
    def metadata_version(self):
        return self.__metadata_version
        
    @property
    def member_name(self):
        return self.__member_name
        
    @property
    def broker_code(self):
        return self.__broker_code
    
    @property
    def broker_branch(self):
        return self.__broker_branch
    
    def make_request(self, uri):
        return urllib2.Request(
            uri,
            headers={
                'user-agent': 'retsquery/{0}'.format(RETSQUERY_VERSION)
            }
        )
    
    def login(self, uri, username, password):
        passwd_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passwd_mgr.add_password(None, uri, username, password)
        auth_handler = patchedurllib2.PatchedHTTPDigestAuthHandler(passwd_mgr)
        cookie_handler = urllib2.HTTPCookieProcessor(self.__cookie_jar)
        
        opener = urllib2.build_opener(auth_handler, cookie_handler)
        urllib2.install_opener(opener)
        response = urllib2.urlopen(self.make_request(uri))
        
        url_parts = urlparse.urlparse(response.geturl())
        #print(url_parts)
        self.base_url = '{0}://{1}'.format(url_parts[0], url_parts[1])
        #print(self.base_url)
        
        self.__is_logged_in = self.__read_login_data(response)
        return self.is_logged_in
        
    def __read_login_data(self, login_response):
        tree = etree.parse(login_response)
        reply_code = tree.xpath('/RETS/@ReplyCode')
        if 1 == len(reply_code) and '0' == reply_code[0]:
            # Successful login
            reply_text = tree.xpath('/RETS/@ReplyText')
            response_text = tree.xpath('/RETS/RETS-RESPONSE/text()')
            return self.__process_response_text(response_text[0])
        return False
        
    def __response_text_to_dict(self, response_text):
        response_text = response_text.strip()
        lines = response_text.splitlines()
        data = {}
        for i in lines:
            j = i.split('=')
            data[j[0]] = j[1]
        return data
    
    def __process_response_text(self, response_text):
        data = self.__response_text_to_dict(response_text)
        parts = data['Broker'].split(',')
        self.__broker_code = parts[0]
        self.__broker_branch = parts[1]
        self.__member_name = data['MemberName']
        parts = data['MinMetadataVersion'].split('.')
        self.__min_metadata_version = [int(i) for i in parts]
        parts = data['MetadataVersion'].split('.')
        self.__metadata_version = [int(i) for i in parts]
        
        if 'MetadataTimestamp' in data:
            self.__metadata_ts = data['MetadataTimestamp']
            
        parts = data['User'].split(',')
        self.__user_id = parts[0]
        self.__user_level = int(parts[1])
        self.__user_class = parts[2]
        self.__agent_code = parts[3]
        
        self.__timeout_seconds = int(data['TimeoutSeconds'])
        
        if 'Action' in data:
            self.__action = data['Action']
            
        if 'ChangePassword' in data:
            self.__change_password = data['ChangePassword']
            
        if 'GetObject' in data:
            self.__get_object = data['GetObject']
            
        if 'Login' in data:
            self.__login = data['Login']
            
        if 'LoginComplete' in data:
            self.__login_complete = data['LoginComplete']
            
        if 'Logout' in data:
            self.__logout = data['Logout']
            
        if 'Search' in data:
            self.__search = data['Search']
            
        if 'GetMetadata' in data:
            self.__get_metadata = data['GetMetadata']
            
        if 'ServerInformation' in data:
            self.__server_information = data['ServerInformation']
            
        if 'Update' in data:
            self.__update = data['Update']
            
        return True

    def make_uri(self, path):
        return urlparse.urljoin(self.base_url, path)
        #print(uri)
        return uri

    def logout(self):
        response = urllib2.urlopen(self.make_request(self.make_uri(self.logout_url)))
        #print(response.read())
        print('Logged out')
    