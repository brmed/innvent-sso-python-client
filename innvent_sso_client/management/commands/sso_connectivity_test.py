# coding: utf-8
import sys

from django.core.management.base import BaseCommand

from innvent_sso_client.utils import SSOAPIClient


class Command(BaseCommand):
    help = 'This command ensures the project can connect to the SSO server.'

    def handle(self, *args, **kwargs):
        client = SSOAPIClient()

        try:
            user = client.get_user('sudo')
            if user is not None:
                self.stdout.write('Connection to SSO server successful.')
                sys.exit(0)
        except Exception:
            pass

        self.stderr.write('Could not connect to SSO server.')
        sys.exit(1)

