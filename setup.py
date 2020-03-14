from setuptools import setup
setup( name='flatpages_index',
       version='0.3',
       description='A small extension for flask_flatpages',
       url='',
       author='Andreas Stephanides',
       author_email='st-andreas@gmx.at',
       packages=['flatpages_index'],
       install_requires=[
           'flask_flatpages','cached_property','python-dateutil'
       ],
       test_suite='nose.collector',
       tests_require=['nose','mock'],
       zip_safe=False)
