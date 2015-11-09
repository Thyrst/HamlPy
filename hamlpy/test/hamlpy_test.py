# -*- coding: utf-8 -*-
import unittest
from nose.tools import eq_, raises
from hamlpy import hamlpy

class HamlPyTest(unittest.TestCase):

    def _test_equal(self, haml, html, rm_lf=False):
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        if rm_lf:
            result = result.replace('\n', '')

        eq_(html, result)

    def test_applies_id_properly(self):
        self._test_equal(
            '%div#someId Some text',
            "<div id='someId'>Some text</div>",
            True
        )

    def test_non_ascii_id_allowed(self):
        self._test_equal(
            u'%div#これはテストです test',
            u"<div id='これはテストです'>test</div>",
            True
        )

    def test_applies_class_properly(self):
        self._test_equal(
            '%div.someClass Some text',
            "<div class='someClass'>Some text</div>",
            True
        )

    def test_applies_multiple_classes_properly(self):
        self._test_equal(
            '%div.someClass.anotherClass Some text',
            "<div class='someClass anotherClass'>Some text</div>",
            True
        )

    def test_dictionaries_define_attributes(self):
        haml = "%html{'xmlns':'http://www.w3.org/1999/xhtml', 'xml:lang':'en', 'lang':'en'}"
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        self.assertTrue("<html" in result)
        self.assertTrue("xmlns='http://www.w3.org/1999/xhtml'" in result)
        self.assertTrue("xml:lang='en'" in result)
        self.assertTrue("lang='en'" in result)
        self.assertTrue(result.endswith("></html>") or result.endswith("></html>\n"))

    def test_dictionaries_support_arrays_for_id(self):
        self._test_equal(
            "%div{'id':('itemType', '5')}",
            "<div id='itemType_5'></div>",
            True
        )

    def test_dictionaries_can_by_pythonic(self):
        self._test_equal(
            "%div{'id':['Article','1'], 'class':['article','entry','visible']} Booyaka",
            "<div id='Article_1' class='article entry visible'>Booyaka</div>",
            True
        )


    def test_html_comments_rendered_properly(self):
        self._test_equal(
            '/ some comment',
            "<!-- some comment -->",
            True
        )

    def test_conditional_comments_rendered_properly(self):
        self._test_equal(
            "/[if IE]\n  %h1 You use a shitty browser",
            "<!--[if IE]>\n  <h1>You use a shitty browser</h1>\n<![endif]-->\n",
        )

    def test_single_line_conditional_comments_rendered_properly(self):
        self._test_equal(
            "/[if IE] You use a shitty browser",
            "<!--[if IE]> You use a shitty browser<![endif]-->\n",
        )

    def test_django_variables_on_tag_render_properly(self):
        self._test_equal(
            '%div= story.tease',
            '<div>{{ story.tease }}</div>',
            True
        )

    def test_stand_alone_django_variables_render(self):
        self._test_equal(
            '= story.tease',
            '{{ story.tease }}',
            True
        )

    def test_stand_alone_django_tags_render(self):
        self._test_equal(
            '- extends "something.html"',
            '{% extends "something.html" %}',
            True
        )

    def test_if_else_django_tags_render(self):
        self._test_equal(
            '- if something\n   %p hello\n- else\n   %p goodbye',
            '{% if something %}\n   <p>hello</p>\n{% else %}\n   <p>goodbye</p>\n{% endif %}\n',
        )

    @raises(TypeError)
    def test_throws_exception_when_trying_to_close_django(self):
        haml = '- endfor'
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)

    def test_handles_dash_in_class_name_properly(self):
        self._test_equal(
            '.header.span-24.last',
            "<div class='header span-24 last'></div>\n",
        )

    def test_handles_multiple_attributes_in_dict(self):
        self._test_equal(
            "%div{'id': ('article', '3'), 'class': ('newest', 'urgent')} Content",
            "<div id='article_3' class='newest urgent'>Content</div>\n",
        )

    def test_inline_tags_are_parsed_correctly(self):
        self._test_equal(
            "-{ url 'main'  } and &{cycle 'odd' 'even' }",
            "{% url 'main' %} and {% cycle 'odd' 'even' %}\n",
        )

    def test_inline_tags_in_attributes_are_parsed_correctly(self):
        self._test_equal(
            "%a{'b': '&{ token } test'} blah",
            "<a b='{% token %} test'>blah</a>\n",
        )

    def test_inline_tags_in_attributes_works(self):
        self._test_equal(
            "%div{'asd':'AA&{filter force_escape|lower }AA'}",
            "<div asd='AA{% filter force_escape|lower %}AA'></div>\n",
        )

    def test_inline_tags_with_arguments_works(self):
        self._test_equal(
            "%a{:href => \"&{ url 'video' video.id }\"}<",
            "<a href='{% url 'video' video.id %}'></a>\n",
        )

    def test_inline_escaping_tags_with_arguments_works(self):
        self._test_equal(
            "%tag{attr: \"\\\&{ url 'video' video.id }\"}<",
            "<tag attr='&{ url \\'video\\' video.id }'></tag>\n",
        )

    def test_inline_tags_escaping_works(self):
        self._test_equal(
            "%p Hi, dude. \\-{firstof v1 v2}, how are you \\&{foo }?",
            "<p>Hi, dude. -{firstof v1 v2}, how are you &{foo }?</p>\n",
        )

    def test_inline_tags_escaping_works_at_start_of_line(self):
        self._test_equal(
            "\\-{block 'asd'}, how are you?",
            "-{block 'asd'}, how are you?\n",
        )

    def test_inline_tags_with_amp_escaping_works_at_start_of_line(self):
        self._test_equal(
            "\\&{name}, how are you?",
            "&{name}, how are you?\n",
        )

    def test_inline_tags_work_at_start_of_line(self):
        self._test_equal(
            "-{bar}, how are you?",
            "{% bar %}, how are you?\n",
        )

    def test_inline_tags_work_with_amp_at_start_of_line(self):
        self._test_equal(
            "&{bar}, how are you?",
            "{% bar %}, how are you?\n",
        )

    def test_inline_tags_with_special_characters_are_parsed_correctly(self):
        self._test_equal(
            u"%span Hi, &{ テスト}",
            u"<span>Hi, {% テスト %}</span>\n",
        )

    def test_inline_variables_are_parsed_correctly(self):
        self._test_equal(
            "={greeting} #{name}, how are you ={date}?",
            "{{ greeting }} {{ name }}, how are you {{ date }}?\n",
        )

    def test_inline_variables_can_use_filter_characters(self):
        self._test_equal(
            "={value|center:\"15\"}",
            "{{ value|center:\"15\" }}\n",
        )

    def test_inline_variables_in_attributes_are_parsed_correctly(self):
        self._test_equal(
            "%a{'b': '={greeting} test'} blah",
            "<a b='{{ greeting }} test'>blah</a>\n",
        )

    def test_inline_variables_in_attributes_work_in_id(self):
        self._test_equal(
            "%div{'id':'package_={object.id}'}",
            "<div id='package_{{ object.id }}'></div>\n",
        )

    def test_inline_variables_in_attributes_work_in_class(self):
        self._test_equal(
            "%div{'class':'package_={object.id}'}",
            "<div class='package_{{ object.id }}'></div>\n",
        )

    def test_inline_variables_in_attributes_are_escaped_correctly(self):
        haml = "%a{'b': '\\\\={greeting} test', title: \"It can't be removed\"} blah"
        html = "<a b='={greeting} test' title='It can\\'t be removed'>blah</a>\n"
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        eq_(sorted(set(html.split())), sorted(set(result.split())))

    def test_inline_variables_escaping_works(self):
        self._test_equal(
            "%h1 Hello, \\#{name}, how are you ={ date }?",
            "<h1>Hello, #{name}, how are you {{ date }}?</h1>\n",
        )

    def test_inline_variables_escaping_works_at_start_of_line(self):
        self._test_equal(
            "\\={name}, how are you?",
            "={name}, how are you?\n",
        )

    def test_inline_variables_with_hash_escaping_works_at_start_of_line(self):
        self._test_equal(
            "\\#{name}, how are you?",
            "#{name}, how are you?\n",
        )

    def test_inline_variables_work_at_start_of_line(self):
        self._test_equal(
            "={name}, how are you?",
            "{{ name }}, how are you?\n",
        )

    def test_inline_variables_with_hash_work_at_start_of_line(self):
        self._test_equal(
            "#{name}, how are you?",
            "{{ name }}, how are you?\n",
        )

    def test_inline_variables_with_special_characters_are_parsed_correctly(self):
        self._test_equal(
            "%h1 Hello, #{person.name}, how are you?",
            "<h1>Hello, {{ person.name }}, how are you?</h1>\n",
        )

    def test_plain_text(self):
        self._test_equal(
            "This should be plain text\n    This should be indented",
            "This should be plain text\n    This should be indented\n",
        )

    def test_plain_text_with_indenting(self):
        self._test_equal(
            "This should be plain text",
            "This should be plain text\n",
        )

    def test_escaped_haml(self):
        self._test_equal(
            "\\= Escaped",
            "= Escaped\n",
        )

    def test_utf8_with_regular_text(self):
        self._test_equal(
            u"%a{'href':'', 'title':'링크(Korean)'} Some Link",
            u"<a href='' title='\ub9c1\ud06c(Korean)'>Some Link</a>\n",
        )

    def test_python_filter(self):
        self._test_equal(
            ":python\n   for i in range(0, 5): print(\"<p>item \%s</p>\" % i)",
            '<p>item \\0</p>\n<p>item \\1</p>\n<p>item \\2</p>\n<p>item \\3</p>\n<p>item \\4</p>\n',
        )

    def test_doctype_html5(self):
        self._test_equal(
            '!!! 5',
            '<!DOCTYPE html>',
            True
        )

    def test_doctype_xhtml(self):
        self._test_equal(
            '!!!',
            '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">',
            True
        )

    def test_doctype_xml_utf8(self):
        self._test_equal(
            '!!! XML',
            "<?xml version='1.0' encoding='utf-8' ?>",
            True
        )

    def test_doctype_xml_encoding(self):
        self._test_equal(
            '!!! XML iso-8859-1',
            "<?xml version='1.0' encoding='iso-8859-1' ?>",
            True
        )

    def test_plain_filter_with_indentation(self):
        self._test_equal(
            ":plain\n    -This should be plain text\n    .This should be more\n      This should be indented",
            "-This should be plain text\n.This should be more\n  This should be indented\n",
        )

    def test_plain_filter_with_no_children(self):
        self._test_equal(
            ":plain\nNothing",
            "Nothing\n",
        )

    def test_filters_render_escaped_backslash(self):
        self._test_equal(
            ":plain\n  \\Something",
            "\\Something\n",
        )

    def test_xml_namespaces(self):
        self._test_equal(
            "%fb:tag\n  content",
            "<fb:tag>\n  content\n</fb:tag>\n",
        )

    def test_attr_wrapper(self):
        haml = """
%html{'xmlns':'http://www.w3.org/1999/xhtml', 'xml:lang':'en', 'lang':'en'}
  %body#main
    %div.wrap
      %a{:href => '/'}
:javascript"""
        hamlParser = hamlpy.Compiler(options_dict={'attr_wrapper': '"'})
        # turn the html tag into a list of attributes so that order doesn't matter
        result = hamlParser.process(haml)
        result_head = result.splitlines()[0][6:][:-1].split(" ")
        result = result[70:]
        correct_head = """<html lang="en" xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">"""[6:][:-1].split(" ")
        self.assertEqual(set(result_head), set(correct_head))
        # all this tab indentation and spacing matters
        self.assertEqual(result,
            '''<body id="main">
    <div class="wrap">
      <a href="/"></a>
    </div>
  </body>
</html>
<script type="text/javascript">
// <![CDATA[
// ]]>
</script>
''')

if __name__ == '__main__':
    unittest.main()
