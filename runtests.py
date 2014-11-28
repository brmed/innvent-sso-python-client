# coding: utf-8
import os
import unittest


if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "testsettings")
    from innvent_sso_client.tests import *
    unittest.main()
