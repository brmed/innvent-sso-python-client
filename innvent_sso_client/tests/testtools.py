# coding: utf-8
import os
from datetime import datetime, timedelta
from mock import Mock, patch

from django.http import QueryDict

from vcr import VCR

from ..utils import sso_hostname, SSOAPIClient


vcr = VCR(
    serializer = 'json',
    cassette_library_dir = os.path.join(os.path.dirname(__file__), 'cassettes'),
    record_mode = 'once',
)


class TestLoginRequiredMixin(object):

    @patch.object(SSOAPIClient, 'retrieve_new_token', Mock(return_value={
        'expires_at': datetime.now() + timedelta(days=1),
        'token': 'this_is_a_token',
    }))
    def test_login_required(self):
        self.client.logout()
        response = self.client.get(self.url)

        qs = QueryDict(None, mutable=True)
        qs['token'] = 'this_is_a_token'
        qs['callback_url'] = 'http://testserver{0}'.format(self.url)
        redirect_url = sso_hostname('/authorize?{0}'.format(qs.urlencode(safe='/')))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], redirect_url)

class TestAjaxLoginRequiredMixin(object):

    def test_login_required(self):
        self.client.logout()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)
