import datetime

from django.utils.safestring import mark_safe

from django.forms.widgets import FileInput, MultiWidget, Select, TextInput


class DatetimeInput(MultiWidget):
    _HOURS = range(0, 24)
    _MINUTES = range(0, 60)
    _FRACTION_MINUTES = range(0, 60, 15)
    USE_FRACTION_MINUTES = 1
    USE_60_MINUTES = 2

    def __init__(self, **kwargs):
        minute_format = kwargs.get('minute_format', self.USE_60_MINUTES)
        attrs = kwargs.get('attrs', None)

        if minute_format == self.USE_60_MINUTES:
            minutes_list = self._MINUTES
        elif minute_format == self.USE_FRACTION_MINUTES:
            minutes_list = self._FRACTION_MINUTES
        else:
            raise ValueError('minute_format must be either USE_FRACTION_MINUTES or USE_60_MINUTES')
        minute_choices = [(minutes, '{:02d}'.format(minutes)) for minutes in minutes_list]
        hour_choices = [(hour, '{:02d}'.format(hour)) for hour in self._HOURS]
        widgets = (TextInput(),
                   Select(choices=hour_choices),
                   Select(choices=minute_choices)
                   )
        super(DatetimeInput, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            if isinstance(value, str):
                value = datetime.datetime.strptime(value, '%d/%m/%Y %H:%M')
            return [value.date().strftime('%d/%m/%Y'), value.hour, value.minute]
        return [None, None, None]

    def format_output(self, rendered_widgets):
        return '{0} - {1}:{2}'.format(*rendered_widgets)

    def value_from_datadict(self, data, files, name):
        datelist = [
            widget.value_from_datadict(data, files, name + '_{}'.format(i))
            for i, widget in enumerate(self.widgets)]
        try:
            date = datetime.datetime.strptime(datelist[0], '%d/%m/%Y')
            value = datetime.datetime(year=date.year, month=date.month, day=date.day,
                                      hour=int(datelist[1]), minute=int(datelist[2]))
        except ValueError:
            return ''
        else:
            return value.strftime('%d/%m/%Y %H:%M')


class ImageInput(FileInput):

    def render(self, name, value, attrs=None):
        file_input = super(ImageInput, self).render(name, value, attrs)
        if value:
            if hasattr(value, 'url'):
                image = "<div class='image-container'><img src='{image_url}'/></div>".format(image_url=value.url)
            else:
                image = ''
        else:
            image = ''
        html = """<div class='imagefield'>
                    {image}
                    {file_input}
                  </div>
               """.format(file_input=file_input, image=image)
        return mark_safe(html)

