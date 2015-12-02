from __future__ import unicode_literals

from mongoengine.errors import ValidationError as mongo_ValidationError
from rest_framework import validators
from rest_framework.exceptions import ValidationError
from rest_framework.compat import unicode_to_repr
from rest_framework_mongoengine.repr import smart_repr

class MongoValidationWrapper():
    def __init__(self, model_field):
        self.field = model_field

    def __call__(self, value):
        try:
            if self.field.validation:
                self.field.validation(value)
            if self.field.validate:
                self.field.validate(value)
        except mongo_ValidationError as e:
            raise ValidationError(e)


class MongoValidatorMixin():
    def exclude_current_instance(self, queryset):
        if self.instance is not None:
            return queryset.filter(pk__ne=self.instance.pk)
        return queryset


class UniqueValidator(MongoValidatorMixin, validators.UniqueValidator):
    def __call__(self, value):
        queryset = self.queryset
        queryset = self.filter_queryset(value, queryset)
        queryset = self.exclude_current_instance(queryset)
        if queryset.first():
            raise ValidationError(self.message.format())

    def __repr__(self):
        return unicode_to_repr('<%s(queryset=%s)>' % (
            self.__class__.__name__,
            smart_repr(self.queryset)
        ))


class UniqueTogetherValidator(MongoValidatorMixin, validators.UniqueTogetherValidator):
    def __call__(self, attrs):
        self.enforce_required_fields(attrs)
        queryset = self.queryset
        queryset = self.filter_queryset(attrs, queryset)
        queryset = self.exclude_current_instance(queryset)
        # Ignore validation if any field is None
        checked_values = [
            value for field, value in attrs.items() if field in self.fields
        ]
        if None not in checked_values and queryset.first():
            field_names = ', '.join(self.fields)
            raise ValidationError(self.message.format(field_names=field_names))


    def __repr__(self):
        return unicode_to_repr('<%s(queryset=%s, fields=%s)>' % (
            self.__class__.__name__,
            smart_repr(self.queryset),
            smart_repr(self.fields)
        ))