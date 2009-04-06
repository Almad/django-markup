from django import forms
from django.conf import settings

JS_EDITOR = 'js/editor.js'
JS_SHOWDOWN = 'js/showdown.js'
CLASS_RICHTEXTAREA = 'rich_text_area'
CSS_RICHTEXTAREA = 'css/editor.css'

class RichTextAreaWidget(forms.Textarea):
    'Widget representing the RichTextEditor.'
    class Media:
        js = (
            settings.ADMIN_MEDIA_PREFIX + JS_EDITOR,
            settings.ADMIN_MEDIA_PREFIX + JS_SHOWDOWN,
        )
        css = {
            'screen': (settings.ADMIN_MEDIA_PREFIX + CSS_RICHTEXTAREA,),
        }

    def __init__(self, height=None, attrs={}):
        css_class = CLASS_RICHTEXTAREA
        if height:
            css_class += ' %s' % height
        super(RichTextAreaWidget, self).__init__(attrs={'class': css_class})

    def render(self, name, value, attrs=None):
        if value and self._field.is_markup():
            src_text = self._field.get_source_text()
        else:
            src_text = value
        return super(RichTextAreaWidget, self).render(name, src_text, attrs)
