import os

try:
    from django.template import TemplateDoesNotExist
    from django.template.loaders import filesystem, app_directories
    _django_available = True
except ImportError:
    class TemplateDoesNotExist(Exception):
        pass

    _django_available = False

from hamlpy import hamlpy
from hamlpy.template.utils import get_django_template_loaders


# Get options from Django settings
options_dict = {}

if _django_available:
    from django.conf import settings
    if hasattr(settings, 'HAMLPY_ATTR_WRAPPER'):
        options_dict.update(attr_wrapper=settings.HAMLPY_ATTR_WRAPPER)

def parse_haml(haml_source):
    hamlParser = hamlpy.Compiler(options_dict=options_dict)
    html = hamlParser.process(haml_source)

    return html


def get_haml_loader(loader):
    if hasattr(loader, 'Loader'):
        baseclass = loader.Loader
    else:
        baseclass = loader

    class Loader(baseclass):

        def get_contents(self, origin):
            haml_source = super(Loader, self).get_contents(origin)
            html = parse_haml(haml_source)

            return html

        def get_template_sources(self, template_name):
            name, _extension = os.path.splitext(template_name)
            extension = _extension.lstrip('.')

            if extension in hamlpy.VALID_EXTENSIONS:
                return super(Loader, self).get_template_sources(template_name)

            else:
                def empty():
                    return
                    yield

                return empty() # returns empty generator

        # deprecated
        def load_template_source(self, template_name, *args, **kwargs):
            name, _extension = os.path.splitext(template_name)
            # os.path.splitext always returns a period at the start of extension
            extension = _extension.lstrip('.')

            if extension in hamlpy.VALID_EXTENSIONS:
                try:
                    haml_source, template_path = super(Loader, self).load_template_source(
                        self._generate_template_name(name, extension), *args, **kwargs
                    )
                except TemplateDoesNotExist:
                    pass
                else:
                    html = parse_haml(haml_source)

                    return html, template_path

            raise TemplateDoesNotExist(template_name)

        load_template_source.is_usable = True

        def _generate_template_name(self, name, extension="hamlpy"):
            return "%s.%s" % (name, extension)

    return Loader


haml_loaders = dict((name, get_haml_loader(loader))
        for (name, loader) in get_django_template_loaders())

if _django_available:
    HamlPyFilesystemLoader = get_haml_loader(filesystem)
    HamlPyAppDirectoriesLoader = get_haml_loader(app_directories)
