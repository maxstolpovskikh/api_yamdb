from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


regex_validator = RegexValidator(regex=r'^[\w.@+-]+\Z')


def validate_not_me(value):
    if value.lower() == 'me':
        raise ValidationError(
            _('Неможет быть me'),
            params={'message': value},
        )
