# -*- coding: utf-8 -*-
import logging


from app.config.settings import _config


class ACLCheck(object):
    def __init__(self, *permissions):
        self.requiredPermissions = permissions

    def hasPermission(self, userid, permission):
        if userid in _config.admins:
            return True

    def __call__(self, origHandler):
      def wrappedHandler(client, message):
        for permission in self.requiredPermissions:
          if not self.hasPermission(message.from_user.id, permission):
            return
        return origHandler(client, message)
      return wrappedHandler