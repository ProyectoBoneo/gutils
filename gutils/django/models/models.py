import datetime

from django.db import models
from django.contrib.auth.models import User

from gutils.django.middleware import get_current_user


class TimestampedModel(models.Model):
    creation_date = models.DateTimeField(blank=True, null=True)
    update_date = models.DateTimeField(blank=True, null=True)

    def set_dates(self):
        now = datetime.datetime.now()
        if self.pk is None:
            self.creation_date = now
        self.update_date = now

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None, ignore_request_data=False):
        if not ignore_request_data:
            self.set_dates()
        return super(TimestampedModel, self).save(force_insert, force_update,
                                                  using, update_fields)

    class Meta:
        abstract = True


class UserModel(models.Model):
    user_created = models.ForeignKey(User, related_name='+', blank=True, null=True)
    user_updated = models.ForeignKey(User, related_name='+', blank=True, null=True)

    def set_user_data(self, user):
        if self.pk is None:
            self.user_created = user
        self.user_updated = user

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None, ignore_request_data=False, user=None):
        if not ignore_request_data:
            if user is None:
                user = get_current_user()
            self.set_user_data(user)
        return super(UserModel, self).save(force_insert, force_update, using, update_fields)

    class Meta:
        abstract = True


class UserTimestampedModel(UserModel, TimestampedModel):

    class Meta:
        abstract = True

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None, ignore_request_data=False, user=None):
        if not ignore_request_data:
            self.set_dates()
        return super(UserTimestampedModel, self).save(force_insert, force_update,
                                                      using, update_fields,
                                                      ignore_request_data, user)


def get_repr(value):
    """
    :param value: valor
    :return: str representation
    """
    if isinstance(value, datetime.date):
        str_repr = value.strftime('%d/%m/%Y')
    elif isinstance(value, datetime.datetime):
        str_repr = value.strftime('%d/%m/%Y %H:%M')
    elif isinstance(value, float):
        str_repr = '{:.2f}'.format(value)
    elif callable(value):
        str_repr = '{}'.format(value())
    elif value is None:
        str_repr = '-'
    else:
        str_repr = str(value)
    return str_repr


def get_field(instance, field):
    """
    :param instance: instance of the model
    :param field: name of the field
    :return: value of the field
    """
    field_path = field.split('.')
    attr = instance
    for elem in field_path:
        try:
            attr = getattr(attr, elem)
        except AttributeError:
            return None
    return attr


def get_model_field_repr(instance, field):
    """
    :param instance: instance of the model
    :param field: name of the field
    :return: str representation of the field
    """
    return get_repr(get_field(instance, field))