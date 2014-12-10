# coding: utf-8
import os

from vcr import VCR


vcr = VCR(
    serializer = 'json',
    cassette_library_dir = os.path.join(os.path.dirname(__file__), 'cassettes'),
    record_mode = 'once',
    match_on = ['method', 'uri', 'port', 'headers', 'body']
)
