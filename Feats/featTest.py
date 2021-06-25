import unittest
from featsBase import get_details


class TestStringMethods(unittest.TestCase):

    def test_get_details(self):
        details = get_details("https://2e.aonprd.com/Feats.aspx?ID=2106")
        self.assertIsNotNone(details["traits"])
        self.assertTrue(details["pfsLegal"])
        self.assertEqual('You\'re an incredible acrobat, evoking wonder and enrapturing audiences with your prowess. It\'s almost a performance! You can roll an  Acrobatics  check instead of a  Performance  check when using the  Perform  action.', details["text"])
        self.assertIn("General", details["traits"])
        self.assertIn("Skill", details["traits"])


if __name__ == '__main__':
    unittest.main()
