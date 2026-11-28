#!/usr/bin/env python3
from __future__ import annotations
import json, pathlib, subprocess, unittest

ROOT = pathlib.Path('/tmp/p24d7-work')

class EvidenceSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cap = json.loads((ROOT/'javascript-capture.json').read_text())
        cls.bin = json.loads((ROOT/'binary64-results.json').read_text())
        cls.mpfr = json.loads((ROOT/'mpfr-results.json').read_text())
        cls.att = json.loads((ROOT/'source-attestation.json').read_text())

    def test_source_attestation_identity_and_hash_stability(self):
        self.assertEqual(self.att['expectedSha'], '941262899a46e54cbf1a94a4da6dd528b8d36780')
        self.assertEqual(self.att['observedSha'], self.att['expectedSha'])
        self.assertEqual(self.att['dirtyStatus'], '')
        self.assertEqual([x['sha256'] for x in self.att['files']], [x['sha256'] for x in self.att['filesAfter']])
        self.assertRegex(self.att['files'][0]['sha256'], r'^[0-9a-f]{64}$')

    def test_operation_order_is_pinned(self):
        self.assertEqual(self.cap['expressions']['degree_radian_order'], 'degrees * Math.PI / 180 (left associative: multiplication then division)')
        self.assertTrue(self.cap['expressions']['rotatePoint']['line'])
        self.assertTrue(self.cap['expressions']['transformLocalPoint']['line'])
        self.assertEqual(len(self.cap['vectors']), 19)
        for v in self.cap['vectors']:
            self.assertIn('rotate', v['source_runtime'])
            self.assertIn('transform', v['source_runtime'])
            self.assertGreater(len(v['rotate']['steps']), 0)
            self.assertGreater(len(v['transform']['steps']), 0)

    def test_binary64_exact_finite_and_midpoints(self):
        self.assertEqual(self.bin['finite_vectors'], self.bin['finite_matches'])
        self.assertEqual(self.bin['finite_vectors'], 40)
        self.assertEqual(len(self.bin['midpoint_tests']), 4)
        for case in self.bin['midpoint_tests']:
            self.assertEqual(case['observed_bits'], case['expected_bits'])

    def test_signed_zero_subnormal_overflow_and_specials_present(self):
        classes = {(r.get('a_class'), r.get('b_class')) for r in self.bin['records']}
        self.assertTrue(any('subnormal' in c for pair in classes for c in pair if c))
        self.assertGreaterEqual(self.bin['special_vectors'], 6)
        self.assertEqual(self.bin['unary_vectors'], 16)
        self.assertEqual(self.bin['comparison_vectors'], 4)

    def test_models_are_separate_and_machine_readable(self):
        self.assertNotEqual((ROOT/'model-a-results.json').read_bytes(), (ROOT/'model-b-stepwise-results.json').read_bytes())
        self.assertEqual(self.mpfr['summary']['vector_count'], len(self.cap['vectors']))
        self.assertIn('source_final_bits', self.mpfr['vectors'][0])
        self.assertIn('mpfr_intervals', self.mpfr['vectors'][0])

    def test_trig_enclosure_results_are_explicit(self):
        summary = self.mpfr['summary']
        self.assertEqual(summary['trig_enclosure_containment_count'], 4)
        self.assertEqual(summary['trig_sin_unique_correct_count'], 17)
        self.assertEqual(summary['trig_cos_unique_correct_count'], 18)
        self.assertLess(summary['trig_enclosure_containment_count'], summary['vector_count'])
        self.assertGreater(len(json.loads((ROOT/'unresolved-cases.json').read_text())['cases']), 0)

    def test_deterministic_capture_serialization(self):
        self.assertEqual((ROOT/'javascript-capture.json').read_bytes(), (ROOT/'javascript-capture-rerun.json').read_bytes())

if __name__ == '__main__':
    unittest.main(verbosity=2)
