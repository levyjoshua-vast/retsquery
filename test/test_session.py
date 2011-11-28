
import unittest
import mox

from src.session import Session, SessionImpl_1_7_2
from src.exceptions import RETSQueryException

class TestSession(mox.MoxTestBase):
    
    def test_create_1_7_2(self):
        sut = Session.create('1.7.2')
        self.assertIsInstance(sut._Session__impl, SessionImpl_1_7_2)
        
    def test_create_bad_version(self):
        with self.assertRaises(RETSQueryException) as mgr:
            Session.create('blah')
            
        self.assertEqual(mgr.exception.message, "'blah' is an invalid or unsupported RETS version number.\nValid versions: 1.7.2")

    def test_login(self):
        mock_impl = self.mox.CreateMockAnything('RETS Imlementation')
        mock_impl.login('some login uri', 'some username', 'some password').AndReturn('some result')
        sut = Session.create(implementation=mock_impl)
        self.mox.ReplayAll()
        result = sut.login('some login uri', 'some username', 'some password')
        self.assertEqual(result, 'some result')
        
    def test_exit_logged_in(self):
        impl = self.mox.CreateMock(SessionImpl_1_7_2)
        sut = Session(impl)
        impl.is_logged_in = True
        impl.logout()
        self.mox.ReplayAll()
        sut.__exit__(None, None, None)
        
    def test_exit_logged_in(self):
        impl = self.mox.CreateMock(SessionImpl_1_7_2)
        sut = Session(impl)
        impl.is_logged_in = False
        self.mox.ReplayAll()
        sut.__exit__(None, None, None)
        