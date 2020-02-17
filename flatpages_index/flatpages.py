from flask_flatpages import FlatPages, pygments_style_defs
import flask_flatpages

#import re

from functools import partial
from werkzeug.utils import cached_property

from collections.abc import Mapping
from .links import Links
from .utils import path_depth, pjoin
from flask_flatpages.flatpages import Page
#Page("asdf","asdf: SAdf","asdf",lambda x: x)


class Page(Page,Mapping):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.links=Links(self)
        self.defaults=self.page_defaults()
        
    def is_subpage(self,root,page_root=""):
        return (self.path.startswith(root["dirpath"]) and  # is a subpage
                path_depth(self.path)<path_depth(root["dirpath"])+2 and   # only one level 
                ( root.path != self.path)
        )

    def __setitem__(self,key,value):
        self.defaults[key]=value
    def __getitem__(self,key):
        if key=="html":
            return self.html
        if key=="links":
            return self.links.todict()
        return self.meta.get(key, self.defaults[key])
    def __iter__(self):
        return iter(self.asdict())
    def __len__(self):
        return len(self.meta)+len(self.defaults)+2

    def asdict(self):
        return {**self.meta,**self.defaults,"html": self.html,"links": self.links.todict()}

    def page_defaults(self, dirpath="."):
        defaults={}
        is_index = (self.path.split('/')[-1]=='index')
        defaults["is_index"]=is_index
        dirpath='/'.join(self.path.split('/')[0:-1]) # remove index from path
        defaults["dirpath"]=dirpath
        if is_index:
            defaults["title"]=self.meta.get("title", dirpath.split('/')[-1])
            if defaults["title"]=="":
                defaults["title"]="Index"
        else:
            defaults["title"]=self.meta.get("title", self.path.split('/')[-1])
        defaults["template"]=self.meta.get("template", FlatPagesIndex.default_template)
        defaults["depth"]=path_depth(self.path)
        defaults["path"]=self.path
        defaults["desc"]=""
        return defaults



flask_flatpages.flatpages.Page=Page

#FileLists=namedtuple("FileLists", ["list_files", "list_images", "sub_pages", "sub_index_pages", "breadcrumbs"])

# Fuction for list all jpg images within the directory




class FlatPagesIndex(FlatPages):
    default_template="page.html"

    def __init__(self,app=None,name=None):
        self.key_pages={}


        super(FlatPagesIndex, self).__init__(app=app, name=name)

        app.config["FLATPAGES_IMAGE_EXTENSIONS"]=["jpg", "jpeg", "JPG"]
    # gets flatpages for an array of paths
    def get_pages(self, paths):
        "get pages for a list of paths"
        if paths is None:
            raise AttributeError("paths for get_pages can't be None")
        return (self.get(p) for p in paths)
        

    # creates a directory based on key metadata that can be added to pages
    @cached_property
    def _key_pages(self):
        d={}
        for path in self._pages:
            if self.config("key")is not None:
                k=self.get(path).meta.get(self.config("key"),None)
                if k is not None:
                    if k in self.key_pages:
                        raise Error("Key: %s is not unique" % k)
                    d[k]=self._pages[path]
 
        return d

    def get_by_key(self,k):
        return self._key_pages.get(k,None)

    @cached_property
    def _pages(self):
        d=super(FlatPagesIndex,self)._pages
        for path in d:
            print(dict(d[path].meta))
            d[path].links.fpi=self
            
            #d[path].defaults=self.page_defaults(d[path])

        return d
    
    def get_sub_pages(self, page):
        return (p for p in self
                if  p.is_subpage(page)
        )
    
 
    def __getitem__(self,key):
        return self.get(key)
        
    # load a page from a path information
    def get(self,path):
        if path == '': path='index'
        page = super(self.__class__,self).get(path) # try to load path
        if page ==None:
            path=pjoin(path,"index")
            page = super(self.__class__,self).get(path) # try to load index page

        return  page
    
