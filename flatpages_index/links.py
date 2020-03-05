"""
This file contains the definition of the Links class. 
This class is a mapping and intended to be used e.g.
"""
from flask import url_for
#from .utils import path_depth,pjoin2,pjoin,list_dir, page_to_link, file_to_link, LinkElement, ImageLinkElement
from .utils import list_dir, pjoin, pjoin2, LinkElement, ImageLinkElement
from functools import partial
from werkzeug.utils import cached_property
from collections import namedtuple
from collections.abc import Mapping
from . import flatpages


def create_link_for(links, pages):
    return []






class Links(Mapping):
    endpoint="index"
    url=lambda s,x: url_for(s.endpoint,name=x)
    file_url=None
    thumb_url=None
    image_url=None
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
    
    @cached_property
    def _getfiles(self):
        """ Load all files in dirpath
        """
        list_dir_md=partial(list_dir, not_ext=[self.fpi.config("EXTENSION"),"~"])
        def add_dirpath(fn):
            return [pjoin(self.page["dirpath"],f) for f in fn]
        
        return  add_dirpath(list_dir_md(self.abspath()))
    @cached_property
    def _getimages(self):
        list_dir_jpg=partial(list_dir, ext=self.fpi.config("IMAGE_EXTENSIONS"), not_ext=["~"])
        def add_dirpath(fn):
            return [pjoin(self.page["dirpath"],f) for f in fn]
        
        return  add_dirpath(list_dir_jpg(self.abspath()))


    def getfiles(self):
        return [LinkElement(n, self.file_url(n), str(n)) for n in self._getfiles]
    def getimages(self):
        return [ImageLinkElement(n, self.image_url(n), str(n),self.thumb_url(n)) for n in self._getimages]
    
    def _get_subpages(self, is_index=False):
        l=[]
        for n in self.fpi.get_sub_pages(self.page):
            if is_index is None or n["is_index"]==is_index:
                l.append(n)
        return l

    @cached_property
    def _subpages(self):
        return self._get_subpages()

    @cached_property
    def _subindexpages(self):
        return self._get_subpages(True)
    
    def getsubpages(self, is_index= False):
        return [self.LinkElement_frompage(n) for n in self._subpages]
                
    def getsubindexpages(self):
        return [self.LinkElement_frompage(n) for n in self._subindexpages]

        
    def todict(self):
        return dict([(i,list(self[i])) for i in self])

 
    def __init__(self, page, endpoint=None,fpi=None):
        self.page=page
        self.endpoint = endpoint or self.__class__.endpoint
        self.fpi= fpi

        fu=lambda s,x: url_for(s.endpoint, name=x)
        
        self.url=self.__class__.url.__get__(self)
        if self.__class__.file_url is None:
            self.file_url=self.url
        else:
            self.file_url=self.__class__.file_url.__get__(self)
        if self.__class__.image_url is None:
            self.image_url=self.url
        else:
            self.image_url=self.__class__.image_url.__get__(self)

        if self.__class__.thumb_url is None:
            self.thumb_url=self.image_url
        else:
            self.thumb_url=self.__class__.thumb_url.__get__(self)

    
        
    def __getitem__(self,key):
        if not isinstance(self.fpi, flatpages.FlatPagesIndex):
            raise TypeError("Must set a FlatPageIndex for links element")
        if key == "breadcrumbs":
            return [self.LinkElement_frompage(i) for i in  self._get_breadcrumbs]
        if key =="files":
            return self.getfiles()
        if key =="subpages":
            return self.getsubpages()
        if key == "subindexpages":
            return self.getsubindexpages()
        if key == "images":
            if self.page["has_img"]:
                return self.getimages()
            return ""
        return []
    def __iter__(self):
        return iter(["images","breadcrumbs","files","subpages","subindexpages"])
    def __len__(self):
        return 5

    def LinkElement_frompage(self,p):
            
        if p.get("image",None) is None:
            return LinkElement(p["title"],self.url(p["url_path"]),p["desc"], None,None,p.get("date", None))
        return    LinkElement(p["title"],self.url(p["url_path"]),p["desc"], self.thumb_url( pjoin(p["dirpath"],p.get("image", None))), pjoin(p["dirpath"],p.get("image", None)),p.get("date", None))
