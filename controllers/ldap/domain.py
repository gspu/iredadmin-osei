#!/usr/bin/env python
# encoding: utf-8

# Author: Zhang Huangbin <michaelbibby (at) gmail.com>

import sys
import web
from web import render
from web import iredconfig as cfg
from controllers.ldap import base
from controllers.ldap.basic import dbinit
from libs.ldaplib import core, admin, domain, attrs

session = web.config.get('_session')

adminLib = admin.Admin()
domainLib = domain.Domain()

#
# Domain related.
#
class list(dbinit):
    '''List all virtual mail domains.'''
    @base.protected
    def GET(self):
        i = web.input()
        result = domainLib.list()
        if result[0] is True:
            allDomains = result[1]
        else:
            return result
        return render.domains(allDomains=allDomains, msg=i.get('msg', None))

    @base.check_global_admin
    @base.protected
    def POST(self):
        i = web.input(domainName=[])
        domainName = i.get('domainName', None)
        if i.has_key('delete'):
            result = domainLib.delete(domainName)
            msg = 'DOMAIN_DELETED_SUCCESS'
        elif i.has_key('disable'):
            result = domainLib.enableOrDisableAccount(domains=domainName, value='disabled',)
            msg = 'DOMAIN_DISABLED_SUCCESS'
        elif i.has_key('enable'):
            result = domainLib.enableOrDisableAccount(domains=domainName, value='active',)
            msg = 'DOMAIN_ENABLED_SUCCESS'
        else:
            msg = i.get('msg', None)

        if result[0] is True:
            web.seeother('/domains?msg=%s' % msg)
        else:
            web.seeother('/domains?msg=%s' % result[1])

class profile(dbinit):
    @base.protected
    def GET(self, profile_type, domain):
        i = web.input()
        self.domain = web.safestr(domain.split('/', 1)[0])
        self.profile_type = web.safestr(profile_type)
        if self.domain == '' or self.domain is None:
            web.seeother('/domains?msg=EMPTY_DOMAIN')

        if self.profile_type not in attrs.DOMAIN_PROFILE_TYPE:
            web.seeother('/domains?msg=INCORRECT_PROFILE_TYPE')

        result = domainLib.profile(domain=self.domain)

        if result[0] is True:
            r = domainLib.list(attrs=['domainName'])
            if r[0] is True:
                allDomains = r[1]
            else:
                return r
            allAdmins = adminLib.list()
            domainAdmins = domainLib.admins(self.domain)

            return render.domain_profile(
                    cur_domain=self.domain,
                    allDomains=allDomains,
                    profile=result[1],
                    profile_type=self.profile_type,
                    admins=allAdmins,
                    # We need only mail address of domain admins.
                    domainAdmins=domainAdmins[0][1].get('domainAdmin', []),
                    msg=i.get('msg', None),
                    )
        else:
            web.seeother('/domains?msg=%s' % result[1])

    @base.protected
    def POST(self, profile_type, domain):
        self.profile_type = web.safestr(profile_type)
        self.domain = web.safestr(domain)

        i = web.input(enabledService=[],)

        result = domainLib.update(
                profile_type=self.profile_type,
                domain=self.domain,
                data=i,
                )
        if result[0] is True:
            web.seeother('/profile/domain/%s/%s?msg=SUCCESS' % (self.profile_type, self.domain) )
        elif result[0] is False:
            web.seeother('/profile/domain/%s/%s?msg=%s' % (self.profile_type, self.domain, result[1]) )

class create(dbinit):
    @base.check_global_admin
    @base.protected
    def GET(self):
        return render.domain_create()

    @base.check_global_admin
    @base.protected
    def POST(self):
        i = web.input()
        result = domainLib.add(data=i)
        if result[0] is True:
            web.seeother('/domains?msg=CREATE_SUCCESS')
        else:
            return render.domain_create(msg=result[1])
