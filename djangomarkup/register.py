from django.conf import settings
from django import forms
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models.fields import Field

from djangomarkup.models import SourceText, TextProcessor

DEFAULT_PROCESSOR = TextProcessor.objects.get(name='markdown')
FIELD_PREFIX = 'djangomarkup_'
__registration_passed = False

class NoopField(Field):
    " Field that does nothing. "

    empty_strings_allowed = True
    def __init__(self, *args, **kwargs):
        kwargs['null'] = True
        Field.__init__(self, *args, **kwargs)
        self.db_column = ''

    def get_attname(self):
        return self.attname

    def get_internal_type(self):
        return 'NoopField'

    def get_db_prep_value(self, value):
        if value is None:
            return None
        return bool(value)

    def formfield(self, **kwargs):
        defaults = {'widget': forms.Textarea}
        defaults.update(kwargs)
        return super(NoopField, self).formfield(**defaults)

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
    registered_models = getattr(settings, 'DJANGO_MARKUP_REGISTERED_FIELDS', [])
    for app_label, model_name, field_name in registered_models:
        cts = ContentType.objects.filter(app_label=app_label, model=model_name)
        if cts.count() < 1:
            continue
        ct = cts[0]
        model_class = ct.model_class()

        if not getattr(model_class, "djangosanetesting_save_wrapped", False):
            new_field_name = '%s%s' % (FIELD_PREFIX, field_name)
            property_name = new_field_name

            # set up virtual_fields
    #        fld = NoopField()
    #        fld.name = new_field_name
    #        fld.attname = ''
    #        model_class._meta.fields.append(fld)

            # set property to the Model class named src_field_name
            prop = generate_property(field_name, ct, property_name)
            setattr(model_class, property_name, prop)
            # handle Model.save own way
            orig_save = model_class.save
            model_class.save = encapsulate_save_method(orig_save, field_name, ct,property_name)

            model_class.djangosanetesting_save_wrapped = True

def modify_registered_admin_options(admin_site):
    if 'django.contrib.admin' not in settings.INSTALLED_APPS:
        return
    registered_models = getattr(settings, 'DJANGO_MARKUP_REGISTERED_FIELDS', [])
    for app_label, model_name, field_name in registered_models:
        cts = ContentType.objects.filter(app_label=app_label, model=model_name)
        if cts.count() < 1:
            continue
        # set property to the Model class named src_field_name
        ct = cts[0]
        model_class = ct.model_class()
        admin_class = admin_site._registry.get(model_class, None)
        if not admin_class:
            return
        # import ipdb;ipdb.set_trace()
        for row in admin_class.fieldsets:
            for item in row:
                if type(item) != dict or 'rich_text_fields' not in item:
                    continue
                new_field_name = '%s%s' % (FIELD_PREFIX, field_name)
                #if field_name in item['fields']:
                if field_name not in item['rich_text_fields']:
                    fields = list(item['fields'])
                    idx = fields.index(field_name)
                    fields[idx] = new_field_name
                    admin_class.opts  # model's _meta property
                    #item['fields'] = tuple(fields)

if __name__ != '__main__' and not __registration_passed:
    from django.contrib.admin.sites import site
    modify_registered_admin_options(site)
    modify_registered_models()
    __registration_passed = True
