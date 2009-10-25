# coding=utf-8
#
# Copyright 2008 Janusz Skonieczny.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import datetime

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext.db import polymodel
from google.appengine.ext.db import Model as BaseModel

from django.db.models import permalink as permalink
from django.template.defaultfilters import slugify
from django.conf import settings
from django.utils.translation import ugettext_lazy as _, ugettext as __

from appenginepatch.ragendja.dbutils import KeyListProperty

import markdown

class TreeNode(polymodel.PolyModel):
    parent_node = db.SelfReferenceProperty(collection_name='children_set')
    ordinal     = db.IntegerProperty()

    def is_root_node(self):
        """ Returns ``True`` if this model instance is a root node, ``False`` otherwise. """
        return self.parent_node is None

    def get_next_sibling(self):
        """ Returns this model instance's next sibling in the tree, or ``None`` if it doesn't have a next sibling. """
        return cls.all().filter("ordinal > ",self.ordinal).order('ordinal').get()

    def get_previous_sibling(self):
        """ Returns this model instance's previous sibling in the tree, or ``None`` if it doesn't have a previous sibling. """
        return cls.all().filter("ordinal < ",self.ordinal).order('-ordinal').get()

    @classmethod
    def get_roots(cls):
        """ Returns the node without parents """
        return cls.all().filter("parent_node =",None)

    def get_children(self):
        """ Returns a ``QuerySet`` containing the immediate children of this model instance, in tree order. """
        return TreeNode.all().filter('parent_node =',self).order("ordinal")        

    POSITIONS = ('first-child', 'last-child', 'left', 'right')

    def move_to(self, target, position='first-child'):
        """
        Moves ``node`` relative to a given ``target`` node as specified by ``position`` (when appropriate), by examining both nodes and
        calling the appropriate method to perform the move.

        A ``target`` of ``None`` indicates that ``node`` should be turned into a root node.

        Valid values for ``position`` are ``'first-child'``, ``'last-child'``, ``'left'`` or ``'right'``.

        ``node`` will be modified to reflect its new tree state in the database.
        """

        if TreeNode.POSITIONS[1] == position:
            self.parent_node = target
            last = self.all().filter("parent_node =", target).order("-ordinal").get()
            if last is not None:
                self.ordinal = last.ordinal + 1
            else:
                ordinal = 1
            self.put()
            return

        parent_node = target.parent_node
        if TreeNode.POSITIONS[3] == position:
            ordinal = target.ordinal + 1

        elif TreeNode.POSITIONS[2] == position:
            ordinal = target.ordinal

        elif TreeNode.POSITIONS[0] == position:
            parent_node = target
            ordinal = 1

        self.parent_node = parent_node
        self.ordinal = ordinal
        movers = self.all().filter("parent_node =", target.parent_node).filter("ordinal >=",self.ordinal).fetch(300,0)
        for n in movers:
            ordinal += 1
            n.ordinal = ordinal
            n.put()
        self.put()


    