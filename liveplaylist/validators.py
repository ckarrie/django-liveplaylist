from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


def validate_wrapper_string(value):
    if '%(stream_url)s' not in value:
        raise ValidationError(
            _('%(value)s needs %(stream_url)s'),
            params={'value': value},
        )
