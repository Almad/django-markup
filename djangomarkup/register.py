from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from djangomarkup.models import SourceText, TextProcessor

DEFAULT_PROCESSOR = TextProcessor.objects.get(name='markdown')
def generate_property(target_field_name, model_content_type, property_name):
    def get_property(self):
        if not self.pk:
            return u'Object was not saved yet.'

        src = None
        try:
            src = SourceText.objects.get(
                content_type=model_content_type,
                object_id=self.pk,
                field=target_field_name,
                processor=DEFAULT_PROCESSOR
            )
        except SourceText.DoesNotExist:
            return u''
        return src.content 

    def set_property(self, value):
        setattr(self, '__value_%s' % property_name, value)

    return property(get_property, set_property)

def encapsulate_save_method(old_save_method, target_field_name, model_content_type, property_name):
    def overriding_save_method(self, **kwargs):
        old_save_method(self, **kwargs)
        attr_name = '__value_%s' % property_name
        new_source = getattr(self, attr_name, None)
        delattr(self, attr_name)
        if new_source is None:
            return

        src, src_created = SourceText.objects.get_or_create(
            content_type=model_content_type,
            object_id=self.pk,
            field=target_field_name,
            processor=DEFAULT_PROCESSOR
        )
        src.content = new_source
        src.save()
        self.__dict__[target_field_name] = src.render()
        old_save_method(self, **kwargs)

    return overriding_save_method

def modify_registered_models():
    registered_models = [('articles', 'article', 'description')]
    for app_label, model_name, field_name in registered_models:
        cts = ContentType.objects.filter(app_label=app_label, model=model_name)
        if cts.count() < 1:
            continue
        # set property to the Model class named src_field_name
        ct = cts[0]
        model_class = ct.model_class()
        property_name = 'src_%s' % field_name
        prop = generate_property(field_name, ct, property_name)
        setattr(model_class, property_name, prop)
        # handle Model.save own way
        orig_save = model_class.save
        model_class.save = encapsulate_save_method(orig_save, field_name, ct,property_name)

# modify_registered_models() should be called in Your urls.py
