from django.core.exceptions import ValidationError

from django import forms


class CUITField(forms.CharField):

    LISTA_VERIFICADORA = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]

    @staticmethod
    def validar_cuit(value):
        value = value.strip()
        if len(value) != 11:
            raise ValidationError('El CUIT debe tener 11 caracteres')
        try:
            int(value)
        except ValueError:
            raise ValidationError('El CUIT debe estar compuesto por 11 números')
        numero_cuit = map(int, value[:10])
        verificador = int(value[10:])
        verificador_correcto = 11 - sum([x*y for (x, y) in zip(CUITField.LISTA_VERIFICADORA, numero_cuit)]) % 11

        if verificador_correcto == 11:
            verificador_correcto = 0

        if verificador_correcto == 10:
            verificador_correcto = 9
        if verificador != verificador_correcto:
            raise ValidationError(
                'El dígito verificador del CUIT es erróneo. Dígito correcto: {}'.format(verificador_correcto))

    def __init__(self, *args, **kwargs):
        kwargs['validators'] = [self.validar_cuit]
        super(CUITField, self).__init__(*args, **kwargs)


class DNIField(forms.CharField):

    @staticmethod
    def validar_dni(value):
        value = value.strip()
        if len(value) > 8:
            raise ValidationError('El DNI no puede contener más de 8 caracteres')
        try:
            int(value)
        except ValueError:
            raise ValidationError('El DNI debe estar compuesto por caracteres numéricos')

    def __init__(self, *args, **kwargs):
        kwargs['validators'] = [self.validar_dni]
        super(DNIField, self).__init__(*args, **kwargs)
