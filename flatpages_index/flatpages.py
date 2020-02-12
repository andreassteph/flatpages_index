from flask_flatpages import FlatPages, pygments_style_defs
import flask_flatpages
from flask import url_for
import re
from .utils import path_depth,pjoin2,pjoin,list_dir, page_to_link, file_to_link
from functools import partial
from werkzeug.utils import cached_property
from collections import namedtuple

FileLists=namedtuple("FileLists", ["list_files", "list_images", "sub_pages", "sub_index_pages", "breadcrumbs"])

# Fuction for list all jpg images within the directory
list_dir_img=partial(list_dir, ext=["jpg", "jpeg","JPG"])


def linklist_dict_lists(filelists):
    for k in filelists:
        filelists[k]=list(filelists[k])
    return filelists

#return {"breadcrumbs": list(filelists.breadcrumbs),
 #           "sub_index_pages": list(filelists.sub_index_pages ),
  #          "sub_pages": list(filelists.sub_pages)  ,
   #         "image_list": list(filelists.list_images),
    ##        "file_list": list(filelists.list_files)
    #}
def my_url(name):
    return name

class FlatPagesIndex(FlatPages):

    def __init__(self,app=None,name=None):
        self.default_template="page.html"
        self.key_pages={}
        super(FlatPagesIndex, self).__init__(app=app, name=name)

    @staticmethod
    def get_breadcrumb_paths(path):
        """
        breadcrumbs decompose the path
        a/b/index -> [a/index a/b/index]
        """
        elements = path.split('/')
#        print "i: %s" % elements

        elements2 = ['index']
        if len(elements)>2:
            for i in range(1,len(elements)):
#                print "i: %s" % elements[0:i]
                elements2.append(pjoin2(elements[0:i])+u'/index')
        return elements2


    def breadcrumbs(self, page):
        "Parse a path or the path of a page into breadcrumbs"
        if type(page) is flask_flatpages.Page:
            return self.get_pages( FlatPagesIndex.get_breadcrumb_paths(page.path))
        else:
            return self.get_pages(FlatPagesIndex.get_breadcrumb_paths(page))

    def get_pages(self, paths):
        "get pages for a list of paths"
        if paths is None:
            raise AttributeError("paths for get_pages can't be None")
        return (self.get(p) for p in paths)

        
    @staticmethod
    def get_paths(pages):
        return (p.path for p in pages)

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
            d[path]=self.page_defaults(d[path])
                        
        return d


    def page_defaults(self, page, dirpath=".", is_index=False):
        is_index = (page.path.split('/')[-1]=='index')
        page.meta["is_index"]=is_index
        dirpath='/'.join(page.path.split('/')[0:-1]) # remove index from path
        page.meta["dirpath"]=dirpath
        if is_index:
            page.meta["title"]=page.meta.get("title", dirpath.split('/')[-1])
        else:
            page.meta["title"]=page.meta.get("title", page.path.split('/')[-1])
        page.meta["template"]=page.meta.get("template", self.default_template)
        page.meta["depth"]=path_depth(page.path)
        page.meta["path"]=page.path

        return page


    
    @staticmethod
    def is_subpage(path,root,page_root=""):
        return (path.startswith(root) and  # is a subpage
                path_depth(path)<path_depth(root)+2 and   # only one level 
                ( page_root != path)
        )
    @staticmethod
    def is_subpage_page(page,root):
        if not "dirpath" in root.meta:
            raise AttributeError("root.meta needs dirpath")
        return (page.path.startswith(root.meta["dirpath"]) and
               path_depth(page.path) < path_depth(root.meta["dirpath"]) +2 and
               root.path != page.path)

    
    @staticmethod
    def is_index_path(path):
        return not ( re.match('.*index',path) is None)

    def get_sub_pages(self, page):
        return (p for p in self
                if  FlatPagesIndex.is_subpage_page(p, page)
                and not FlatPagesIndex.is_index_path(p.path)
        )
    
    # List all index subpages of the current page i.e. all pages in subdirectories
    def get_sub_ipages(self, page ):
        return (p for p in self
                if FlatPagesIndex.is_subpage_page(p, page)
                and FlatPagesIndex.is_index_path(p.path)
        )
 
    def __getitem__(self,key):
        return self.get(key)
        
    # load a page from a path information
    def get(self,path):
        if path == '': path='index'
        page = super(self.__class__,self).get(path) # try to load index page
        if page ==None:
            path=pjoin(path,"index")
            page = super(self.__class__,self).get(path) # try to load index page
        return  page
    def fpget(self,name):
        return self.get(name) 
    
    def _load_linklist(self,page,page_url_for=my_url,file_url_for=my_url):
        fl={}
        abspath = pjoin(self.config("root"),page.meta["dirpath"])
        fl["breadcrumbs"] = page_to_link( self.breadcrumbs(page.path), page_url_for)
        if (page.meta.get("has_img",False) ):
            fl["list_images"] = file_to_link(list_dir_img(abspath), page_url_for)
        if page.meta["is_index"] or page.meta.get("has_files",False):
            # List all non *.md files within the directory
            list_dir_md=partial(list_dir, not_ext=[self.config("EXTENSION"),"~"])
            fl["list_files"] = file_to_link(list_dir_md(abspath), file_url_for)
        if page.meta.get("is_index",False):
            fl["sub_pages"] = page_to_link(self.get_sub_pages(page), page_url_for)
            fl["sub_index_pages"] = page_to_link(self.get_sub_ipages(page), page_url_for)

        return fl
    
    def linklists(self,page,page_url_for=my_url,file_url_for=my_url):
        #return self._load_linklist(page,page_url_for)
        return linklist_dict_lists(self._load_linklist(page,page_url_for,file_url_for))
