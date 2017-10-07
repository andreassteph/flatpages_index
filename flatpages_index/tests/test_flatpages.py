import unittest
from flatpages_index import FlatPagesIndex, LinkElement
from flask_flatpages import FlatPages
from mock import patch, Mock
from flask import Flask

class TestFlatpages(unittest.TestCase):
    def setUp(self):
        app = Flask(__name__)
        app.config.update({"FLATPAGES_ROOT":".", "FLATPAGES_EXTENSION": ".md","FLATPAGES_KEY": "key"})
#        app.config("FLATPAGES_EXTENSION") = '.md'  
#        app.config("FLATPAGES_INDEX") = 'index'

        self.fp=FlatPagesIndex(app)
        d={}
        for p in ["test/index", "page1", "index", "test/test2/index", "test/test2/page4", "test2/page0","test/page2", "test/page3"]:
            m=Mock()
            m.path=p
            m.meta={}
            if p == "page1":
                m.meta["key"]="key1"
            d[p]=m
        self.pages=d

    def test_get_by_key(self):
        with patch.object(FlatPages,"_pages", self.pages):
            self.fp[""]
            p1 =self.fp["page1"]
            p=self.fp.get_by_key("key1")
            self.assertIsNot(p,None)
            self.assertIs(p,p1)
    def test_p(self):
        self.assertEquals(FlatPagesIndex.get_breadcrumb_paths(""),['index'])
        self.assertEquals(FlatPagesIndex.get_breadcrumb_paths("index"),['index']) 

    def test_subpages(self):
        with patch.object(FlatPages,"_pages", self.pages):
            p=self.fp.get("index")
            spgs=self.fp.get_sub_pages(p)
            self.assertEquals([p.path for p in spgs],["page1"])

    def test_subipages(self):
        with patch.object(FlatPages,"_pages", self.pages):
            p=self.fp.get("index")
            spgs=list(self.fp.get_sub_ipages(p))
            self.assertEquals([p.path for p in spgs],["test/index"])
            self.assertEquals([p.meta["title"] for p in spgs],["test"])

    def test_linklist(self):
        with patch("os.listdir") as mock_listdir:
            with patch("os.path.isfile") as mock_isfile:
                with patch.object(FlatPages,"_pages", self.pages):
                    mock_listdir.return_value=["test.jpg", "test.md"]
                    mock_isfile=True
 
                    p=self.fp.get("index")
                    fl=self.fp.linklists(p)
                    self.assertTrue("breadcrumbs" in fl)
                    self.assertTrue("sub_pages" in fl)
                    self.assertTrue("sub_index_pages" in fl)
                    self.assertTrue("list_files" in fl)
                    self.assertFalse("list_images" in fl)
                    self.assertEqual(fl["list_files"], [LinkElement(title="test.jpg",url="test.jpg", desc='')])
                    self.assertEqual(fl["sub_pages"], [LinkElement(title="page1",url="page1", desc='')])
    def test_get(self):
        with patch.object(FlatPages,"_pages", self.pages):
            
            p=self.fp.fpget("index")
            p2=self.fp.get("index")
            self.assertIs(p,p2)
            self.assertIsNot(p,None)
            p2=self.fp["index"]
            self.assertIs(p,p2)
            p2=self.fp[""]
            self.assertIs(p,p2)


if __name__ == '__main__':
    unittest.main()
