"""Tests for the utils."""

import os
import json
from unittest import TestCase

from infdata.utils import generate_metadata_template, normalize


class TestMetadataSuggestion(TestCase):
    def test_returns_right_metadata(self):

        data = json.load(
            open(os.path.join(os.getcwd(), 'tests/testdata/records.json'), 'rb'))

        metadata = generate_metadata_template(data)

        self.assertEqual(
            metadata[0]['地址']['原始基金'],
            {'': [['str'], []]}
        )

        # Add some rules to metadata generated
        metadata[0]['地址']['原始基金'][''][0][0] = 'float'
        metadata[0]['地址']['原始基金'][''][0].append("lambda x: 10**4 * float(x.replace('万元', ''))")
        metadata[0]['地址']['原始基金'][''][1].append('https://www.wikidata.org/wiki/Q39099')


        # Ensure that we have expected result: 
        newdata = normalize(metadata+data)
        self.assertEqual(newdata[0]['地址']['Q39099'], float(4000000))
