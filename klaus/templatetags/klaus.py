# -*- coding: utf-8 -*-
import re

from django import template

register = template.Library()


@register.filter
def shorten_sha1(sha1):
    if re.match('[a-z\d]{20,40}', sha1):
        sha1 = sha1[:10]
    return sha1
