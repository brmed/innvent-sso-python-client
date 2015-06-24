# coding: utf-8
import sys
from os.path import join, dirname

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


class Tox(TestCommand):

    user_options = TestCommand.user_options + [
        ('environment=', 'e', "Run 'test_suite' in specified environment")
    ]
    environment = None

    def finalize_options(self):
        super(Tox, self).finalize_options()
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import tox
        if self.environment:
            self.test_args.append('-e{0}'.format(self.environment))

        errno = tox.cmdline(self.test_args)
        sys.exit(errno)


setup(
    name='innvent-sso-python-client',
    version='0.4.0',
    description='Python Client for Innvent SSO',
    author='Innvent',
    author_email='desenvolvimentobrmed@innvent.com.br',
    url='https://github.com/innvent/innvent-sso-python-client',
    packages=find_packages(),
    test_suite='innvent_sso_client.tests',
    install_requires=['Django>=1.5.3', 'requests>=2.4.1', 'python-dateutil==1.5'],
    tests_require=['tox>=1.6.1', 'virtualenv>=1.11.2'],
    cmdclass = {'test': Tox},
)
