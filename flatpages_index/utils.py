"""
Utility Functions for handling files and paths
"""
import os
import re
from os.path import isfile, abspath

from collections import namedtuple
LinkElement=namedtuple("LinkElement", ["title", "url","desc"])

def pjoin2 (pth):
     if (not type(pth) is list):
          raise AttributeError("path should be a list") 
     pth=filter(lambda s: len(s.strip())>0, pth)
     if len(pth)==0:
          raise AttributeError("List for pjoin2 can't be empty")
     return u'/'.join(pth) or u''

def pjoin (rt,pth):
    return pjoin2([rt,pth])

def list_dir(mypath,ext=None, not_ext=None):
    return (f for f in os.listdir(mypath)
            if os.path.isfile(os.path.join(mypath, f))
            and ((re.match('.*%s$' % not_ext, f) is None) or (not_ext is None))
            and ((re.match('.*%s$' % ext, f) is not None) or (ext is None))
    )

def path_depth(path):
    if path =="":
        return 0
    p_split=path.split('/')
    cc=len(p_split)
    if p_split[-1]=='index' or p_split[-1]=='index.json' :
        cc=cc-1
    return cc

def page_to_link(pages, url_for_method):
     "page to url"
     for p in pages:
          yield LinkElement(title=p.meta.get("title",p.path),
                            url=url_for_method(name=p.path),
                            desc='/'.join(p.path.split('/')[-2:-1])
          )
def file_to_link(files, url_for_method):
     "file to url"
     for p in files:
          yield LinkElement(title=p,
                            url=url_for_method(name=p),
                            desc=""
          )
