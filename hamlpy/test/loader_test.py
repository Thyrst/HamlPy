import unittest
import sys
import os

try:
  from django.conf import settings

  settings.configure(DEBUG=True, TEMPLATE_DEBUG=True)
except ImportError as e:
  pass

from hamlpy.template.loaders import get_haml_loader, TemplateDoesNotExist

class Origin(object):
    def __init__(self, name='', template_name='', loader=None):
        self.name=name
        self.template_name=template_name
        self.loader = loader

class DummyLoader(object):
    """
    A dummy template loader that only loads templates from self.templates
    """
    dirs = (
        'templates/loader1',
        'templates/loader2',
        'templates/loader3',
    )

    def __init__(self, *args, **kwargs):
        self.Loader = self.__class__

    def get_contents(self, origin):
        with open(origin.name, 'r') as f:
            return f.read()
    
    def get_template_sources(self, template_name, template_dirs=None):
        for directory in self.dirs:
            filename = directory + '/' + template_name

            if os.path.isfile(filename):
                yield Origin(
                        name=filename,
                        template_name=template_name,
                        loader=self,
                )

    def load_template_source(self, template_name, *args, **kwargs):
        for origin in self.get_template_sources(template_name):
            try:
                return self.get_contents(origin), origin.name
            except TemplateDoesNotExist:
                pass
        raise TemplateDoesNotExist(template_name)

class LoaderTest(unittest.TestCase):
    """
    Tests for the django template loader.
    
    A dummy template loader is used that loads only from a dictionary of templates.
    """
    
    def setUp(self): 
        dummy_loader = DummyLoader()
        
        hamlpy_loader_class = get_haml_loader(dummy_loader)
        self.hamlpy_loader = hamlpy_loader_class()
    
    def _test_assert_exception(self, template_name):
        try:
            self.hamlpy_loader.load_template_source(template_name)
        except TemplateDoesNotExist:
            self.assertTrue(True)
        else:
            self.assertTrue(False, '\'%s\' should not be loaded by the hamlpy template loader.' % template_name)
    
    def test_file_not_in_dict(self):
        # not_in_dict.txt doesn't exit, so we're expecting an exception
        self._test_assert_exception('not_in_dict.hamlpy')
    
    def test_file_in_dict(self):
        # test5.html in in dict, but with an extension not supported by
        # the loader, so we expect an exception
        self._test_assert_exception('test5.html')
    
    def test_file_should_load(self):
        # loader_test.hamlpy is in the dict, so it should load fine
        try:
            self.hamlpy_loader.load_template_source('test1.haml')
        except TemplateDoesNotExist:
            self.assertTrue(False, '\'test1.haml\' should be loaded by the hamlpy template loader, but it was not.')
        else:
            self.assertTrue(True)
    
    def test_file_different_extension(self):
        # test4.haml is in dict, but we're going to try
        # to load test4.html
        # we expect an exception since the extension is not supported by
        # the loader
        self._test_assert_exception('test4.html')

    def test_get_template_sources(self):
        self.assertTrue(False, 'Finish the test!')

    def test_get_contents(self):
        content = False
        for origin in self.hamlpy_loader.get_template_sources('test3.haml'):
            try:
                content = self.hamlpy_loader.get_contents(origin)
                break
            except TemplateDoesNotExist:
                pass

        self.assertTrue(bool(content), '.get_template_sources hasn\'t found \'test3.haml\'')
        self.assertEqual(content, '<h2>{{ var }}</h2>\n')
