
import urllib2
import unittest
from StringIO import StringIO
import cookielib
import urllib2
import urlparse

import mox

from src.session import SessionImpl_1_7_2
import src.patchedurllib2

class TestSessionImpl_1_7_2(mox.MoxTestBase):
    
    def test__init__(self):
        sut = SessionImpl_1_7_2()
        self.assertIsInstance(sut._SessionImpl_1_7_2__cookie_jar, cookielib.CookieJar)
    
    def test_login(self):
        
        self.mox.StubOutClassWithMocks(urllib2, 'Request')
        request = urllib2.Request(
            'some login uri',
            headers={ 'user-agent': 'retsquery/0.0.1' }
        )
        
        self.mox.StubOutClassWithMocks(urllib2, 'HTTPPasswordMgrWithDefaultRealm')
        passwd_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passwd_mgr.add_password(None, 'some login uri', 'some username', 'some password')
        
        self.mox.StubOutClassWithMocks(src.patchedurllib2, 'PatchedHTTPDigestAuthHandler')
        auth_handler = src.patchedurllib2.PatchedHTTPDigestAuthHandler(passwd_mgr)
        
        self.mox.StubOutClassWithMocks(urllib2, 'HTTPCookieProcessor')
        cookie_processor = urllib2.HTTPCookieProcessor(mox.IsA(cookielib.CookieJar))
        
        self.mox.StubOutWithMock(urllib2, 'build_opener')
        urllib2.build_opener(auth_handler, cookie_processor).AndReturn('some opener')
        
        self.mox.StubOutWithMock(urllib2, 'install_opener')
        urllib2.install_opener('some opener')
        
        self.mox.StubOutWithMock(urllib2, 'urlopen')
        some_response = self.mox.CreateMockAnything()
        urllib2.urlopen(request).AndReturn(some_response)
        some_response.geturl().AndReturn('some url')
        
        sut = SessionImpl_1_7_2()
        self.mox.StubOutWithMock(sut, '_SessionImpl_1_7_2__read_login_data')
        sut._SessionImpl_1_7_2__read_login_data(some_response).AndReturn(True)
        
        self.mox.ReplayAll()
        self.assertTrue(sut.login('some login uri', 'some username', 'some password'))
        
    def test_get_metadata(self):
        sut = SessionImpl_1_7_2()
        sut.scheme = 'http'
        sut.netloc = 'www.example.com'
        sut.get_metadata_url = '/GetMetadata.asmx/GetMetadata'
        self.mox.StubOutWithMock(sut, 'make_request')
        request = self.mox.CreateMock(urllib2.Request)
        request.headers = 'some headers'
        sut.make_request('http://www.example.com/GetMetadata.asmx/GetMetadata?Type=METADATA-SYSTEM&ID=%2A').AndReturn(request)
        self.mox.StubOutWithMock(urllib2, 'urlopen')
        urllib2.urlopen(request).AndReturn(StringIO('some result'))
        self.mox.ReplayAll()
        sut.get_metadata()
        self.mox.VerifyAll()

class TestSessionImpl_1_7_2__process_response_text(mox.MoxTestBase):
    
    def test(self):
        
        response_text = """
MemberName=some user name
User=some user id,12345,some user class,some agent code
Broker=,50477
MetadataVersion=4.5.6
MinMetadataVersion=1.2.3
TimeoutSeconds=18000
ChangePassword=some change password url
GetObject=some getobject url
Login=some login url
Logout=some logout url
Search=some search url
GetMetadata=some getmetadata url
"""

        sut = SessionImpl_1_7_2()
        self.assertTrue(sut._SessionImpl_1_7_2__process_response_text(response_text))
        self.assertEqual(sut.broker_code, '')
        self.assertEqual(sut.broker_branch, '50477')
        self.assertEqual(sut.member_name, 'some user name')
        self.assertEqual(sut.min_metadata_version, [1,2,3])
        self.assertEqual(sut.metadata_version, [4,5,6])
        self.assertEqual(sut.user_id, 'some user id')
        self.assertEqual(sut.user_level, 12345)
        self.assertEqual(sut.user_class, 'some user class')
        self.assertEqual(sut.agent_code, 'some agent code')
        self.assertEqual(sut.timeout_seconds, 18000)
        
        self.assertEqual(sut.action_url, None)
        self.assertEqual(sut.change_password_url, 'some change password url')
        self.assertEqual(sut.get_object_url, 'some getobject url')
        self.assertEqual(sut.login_url, 'some login url')
        self.assertEqual(sut.login_complete_url, None)
        self.assertEqual(sut.logout_url, 'some logout url')
        self.assertEqual(sut.search_url, 'some search url')
        self.assertEqual(sut.get_metadata_url, 'some getmetadata url')
        self.assertEqual(sut.server_information_url, None)
        self.assertEqual(sut.update_url, None)

class TestSessionImpl_1_7_2__read_login_data(mox.MoxTestBase):
    
    def test_normal(self):
        
        login_response = StringIO("""\
<?xml version="1.0" encoding="utf-8"?>
<RETS ReplyCode="0" ReplyText="some reply text">
  <RETS-RESPONSE>
some response text
</RETS-RESPONSE>
</RETS>
""")
        
        sut = SessionImpl_1_7_2()
        self.mox.StubOutWithMock(sut, '_SessionImpl_1_7_2__process_response_text')
        sut._SessionImpl_1_7_2__process_response_text('\nsome response text\n').AndReturn(True)
        self.mox.ReplayAll()
        self.assertTrue(sut._SessionImpl_1_7_2__read_login_data(login_response))
        
    def test_no_reply_code(self):
        
        login_response = StringIO("""\
<?xml version="1.0" encoding="utf-8"?>
<RETS></RETS>
""")
        
        sut = SessionImpl_1_7_2()
        self.mox.ReplayAll()
        result = sut._SessionImpl_1_7_2__read_login_data(login_response)
        self.assertIsNotNone(result)
        self.assertFalse(result)
        
    def test_bad_reply_code(self):
        
        login_response = StringIO("""\
<?xml version="1.0" encoding="utf-8"?>
<RETS ReplyCode="blah"></RETS>
""")
        
        sut = SessionImpl_1_7_2()
        self.mox.ReplayAll()
        result = sut._SessionImpl_1_7_2__read_login_data(login_response)
        self.assertIsNotNone(result)
        self.assertFalse(result)
