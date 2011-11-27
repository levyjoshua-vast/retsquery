
import urllib2
import re

class PatchedHTTPDigestAuthHandler(urllib2.HTTPDigestAuthHandler):

    def http_error_auth_reqed(self, auth_header, host, req, headers):
        authreq = headers.get(auth_header, None)
        if self.retried > 5:
            # Don't fail endlessly - if we failed once, we'll probably
            # fail a second time. Hm. Unless the Password Manager is
            # prompting for the information. Crap. This isn't great
            # but it's better than the current 'repeat until recursion
            # depth exceeded' approach <wink>
            raise urllib2.HTTPError(req.get_full_url(), 401, "digest auth failed",
                                    headers, None)
        else:
            self.retried += 1
        if authreq:
            # This is the code that doesn't work if the server supplies both
            # digest and basic authentication data in the www-authenticate
            # header.
            #
            # scheme = authreq.split()[0]
            # if scheme.lower() == 'digest':
            #    return self.retry_http_digest_auth(req, authreq)
            #
            # Replaced it with this...
            matches = re.search(r'digest\s', authreq, re.IGNORECASE)
            if matches:
                return self.retry_http_digest_auth(req, authreq)
                