# Copyright (c) 2013, The DjaoDjin Team
# All rights reserved.

"""
Convenience module for access of djaodjin-answers application settings,
# which enforces default settings when the main settings module does not
contain the appropriate settings.
"""
from django.conf import settings

OBJECT_TITLE = getattr(settings, 'ANSWERS_OBJECT_TITLE', 'question')
