"""Redirects from removed ``/leads/`` URLs to the integrated CRM under ``/new-lead/``."""

import re

from django.shortcuts import redirect


_LEAD_UUID = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.I)


def redirect_legacy_leads_path(request, subpath):
    """Map old ``/leads/<subpath>`` URLs to ``/new-lead/...``."""
    subpath = (subpath or '').strip('/')
    if not subpath:
        return redirect('/new-lead/leads/')

    head, _, tail = subpath.partition('/')
    rest = tail.strip('/') if tail else ''

    if head == 'dashboard':
        return redirect('/new-lead/')
    if head == 'sales-team':
        return redirect('/new-lead/team/users/')
    if head == 'create':
        return redirect('/new-lead/leads/create/')
    if head == 'export':
        return redirect('/new-lead/leads/export/')
    if _LEAD_UUID.match(head) and not rest:
        return redirect(f'/new-lead/leads/{head}/')
    if _LEAD_UUID.match(head) and rest:
        suffix = f'{head}/{rest}'.rstrip('/')
        return redirect(f'/new-lead/leads/{suffix}/')

    return redirect('/new-lead/' + subpath.rstrip('/') + '/')
