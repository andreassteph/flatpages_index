import os
import unittest
from flatpages_index import utils
from mock import patch
class TestUtils(unittest.TestCase):
    def test_pjoin2(self):
        self.assertEquals(utils.pjoin2(["a","b"]),"a/b")
        self.assertEquals(utils.pjoin2(["b"]),"b")
        self.assertEquals(utils.pjoin2(["b",""]),"b")
        self.assertEquals(utils.pjoin2(["","b"]),"b")
        with self.assertRaises(AttributeError):
            utils.pjoin2("sdf")
        with self.assertRaises(AttributeError):
            utils.pjoin2([""])

    def test_pjoin(self):
        self.assertEquals(utils.pjoin("a","b"), "a/b")
        self.assertEquals(utils.pjoin("a",""),"a")
        with self.assertRaises(AttributeError):
            utils.pjoin("sdf",[])
    def test_list_dir(self):
        with patch("os.listdir") as mock_listdir:
            with patch("os.path.isfile") as mock_isfile:
                mock_listdir.return_value=["test.jpg"]
                mock_isfile=True
                self.assertEquals(list(os.listdir("s")),["test.jpg"])
                self.assertEquals(list(utils.list_dir("s")), ["test.jpg"])
            
                
                
                
if __name__ == '__main__':
    unittest.main()
