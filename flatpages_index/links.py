"""
This file contains the definition of the Links class. 
This class is a mapping and intended to be used e.g.
"""
from flask import url_for
#from .utils import path_depth,pjoin2,pjoin,list_dir, page_to_link, file_to_link, LinkElement, ImageLinkElement
from datetime import datetime
from functools import partial
from werkzeug.utils import cached_property
from cached_property import cached_property_with_ttl
from collections import namedtuple
from collections.abc import Mapping
from . import flatpages
from .utils import list_dir, pjoin, pjoin2, LinkElement, ImageLinkElement


def create_link_for(links, pages):
    return []





class Links(Mapping):
    url=lambda self,x: x
    file_url=lambda self,x: self.url(x)
    thumb_url=lambda self,x: self.url(x)
    image_url=lambda self,x: self.url(x)
    """
    This class should be smart about loading relative links to a page.
    1. Breadcrumbs
    Breadcumbs are all upper pages that could be linked
    links["files"]
    links["images"]
    links["subpages"]
    links["subindexpages"]
    """
    @cached_property
    def _get_breadcrumbs(self):
        """
          Parse a path or the path of a page into breadcrumbs
          breadcrumbs decompose the path
          a/b/index -> [a/index a/b/index]
        """
        path=self.page.path
        if not type(path) is str:
            raise TypeError( "Link path must be a string i.e. a path")

        path_elements = path.split('/')
        elements2 = [self.fpi.get("index")]
        if len(path_elements)>=2:
            for i in range(1,len(path_elements)):
                p=pjoin2(path_elements[0:i])
                pg=self.fpi.get(p)
                if pg is None:
                    raise ValueError("For path %s no Page found"% p)
                elements2.append(pg)

        return elements2

    def abspath(self):
        return pjoin(self.fpi.config("root"),self.page["dirpath"])
    
    @cached_property_with_ttl(5)
    def _getfiles(self):
        """ Load all files in dirpath
        """
        list_dir_md=partial(list_dir, not_ext=[self.fpi.config("EXTENSION"),"~"])
        def add_dirpath(fn):
            return [pjoin(self.page["dirpath"],f) for f in fn]
        
        return  add_dirpath(list_dir_md(self.abspath()))

    @cached_property_with_ttl(5)
    def _getimages(self):
        list_dir_jpg=partial(list_dir, ext=self.fpi.config("IMAGE_EXTENSIONS"), not_ext=["~"])
        def add_dirpath(fn):
            return [pjoin(self.page["dirpath"],f) for f in fn]
        
        return  add_dirpath(list_dir_jpg(self.abspath()))


 
    def _get_subpages(self, is_index=False):
        l1=[]
        l2=[]
        for n in self.fpi.get_sub_pages(self.page):
            if is_index is None or n["is_index"]==is_index:
                if not n.get("date",None) is None:
                    l1.append(n)
                else:
                    l2.append(n)
                
        def sort_key_date(p):
            return datetime.strptime(p.get("date",0), '%d.%m.%Y')
        def sort_key_title(p):
            return p.get("title","ZZZZZZZZZ")
        
        l1.sort(key=sort_key_date, reverse=True)
        l2.sort(key=sort_key_title)
        return l1+l2

    @cached_property_with_ttl(5)
    def _subpages(self):
        return self._get_subpages()

    @cached_property_with_ttl(5)
    def _subindexpages(self):
        return self._get_subpages(True)
    
       
    def todict(self):
        return dict([(i,list(self[i])) for i in self])

 
    def __init__(self, page, endpoint=None,fpi=None):
        self.page=page
        self.fpi= fpi

        
        self.url=self.__class__.url.__get__(self)
        self.file_url=self.__class__.file_url.__get__(self)
        self.image_url=self.__class__.image_url.__get__(self)
        self.thumb_url=self.__class__.thumb_url.__get__(self)

    
    def __getattr__(self,item):
        if item in self:
            return self.__getitem__(item)    
        #raise AttributeError()
    def __getitem__(self,key):
        if not isinstance(self.fpi, flatpages.FlatPagesIndex):
            raise TypeError("Must set a FlatPageIndex for links element")
        if key == "breadcrumbs":
            return [self.LinkElement_frompage(i) for i in  self._get_breadcrumbs]
        if key =="files":
            return [LinkElement(n, self.file_url(n), str(n),"","","") for n in self._getfiles]
        if key =="subpages":
            return [self.LinkElement_frompage(n) for n in self._subpages]
        if key == "subindexpages":
            return [self.LinkElement_frompage(n) for n in self._subindexpages]
        if key == "images":
            #if "has_img" in self.page and self.page["has_img"]:
            return self.getimages()
            #return ""
        return []
    def __iter__(self):
        return iter(["images","breadcrumbs","files","subpages","subindexpages"])
    def __len__(self):
        return 5

    def LinkElement_frompage(self,p):
        img = p.get("image",None)
        if img:
            img=self.thumb_url(pjoin(p["dirpath"],p.get("image", None)))
        if img is None and len(p.links["images"])>0:
            img = p.links["images"][0].thumb_url
        if img is None:
            return LinkElement(p["title"],self.url(p["url_path"]),p["desc"], None,None,p.get("date", None))
        return    LinkElement(p["title"],self.url(p["url_path"]),p["desc"], img, img,p.get("date", None))
    #
    #depricated 
    def getfiles(self):
        return [LinkElement(n, self.file_url(n), str(n),"","","") for n in self._getfiles]
    def getimages(self):
        return [ImageLinkElement(n, self.image_url(n), str(n),self.thumb_url(n)) for n in self._getimages]
    def getsubpages(self, is_index= False):
        return [self.LinkElement_frompage(n) for n in self._subpages]                
    def getsubindexpages(self):
        return [self.LinkElement_frompage(n) for n in self._subindexpages]

    