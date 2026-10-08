import importlib.util, json, threading, unittest, urllib.request, urllib.error
from pathlib import Path
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("app",ROOT/"main.py")
radar=importlib.util.module_from_spec(spec)
spec.loader.exec_module(radar)

class RadarTests(unittest.TestCase):
    def test_sources_and_matching(self):
        p=json.loads((ROOT/'papers.json').read_text()); results=radar.rank(p,'2026-10-08')
        self.assertEqual(len(results),3); self.assertTrue(all(x['matched_terms'] for x in results))
        self.assertIn('2026-09-30',radar.report(p,'2026-10-08'))
    def test_future_and_duplicate_excluded(self):
        p=json.loads((ROOT/'papers.json').read_text()); future={**p[0],'url':'https://example.invalid','published':'2027-01-01'}
        self.assertEqual(len(radar.rank(p+[p[0],future],'2026-10-08')),3)

if __name__=="__main__": unittest.main()
