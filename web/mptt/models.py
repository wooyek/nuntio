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
    parent_node     = db.SelfReferenceProperty(collection_name='children_set')
    right_no        = db.IntegerProperty()
    left_no        = db.IntegerProperty()

    def is_root_node(self):
        """ Returns ``True`` if this model instance is a root node, ``False`` otherwise. """
        return self.parent_node is None

    def get_descendant_count(self):
        """ Returns the number of descendants this model instance has. """
        return ((self.right_no - self.left_no) - 1) / 2        

    def is_leaf_node(self):
        """ Returns ``True`` if this model instance is a leaf node (it has no children), ``False`` otherwise. """
        return self.get_descendant_count() < 1        

    def get_ancestors(self, ascending=False):
        """
        Creates a ``QuerySet`` containing the ancestors of this model
        instance.

        This defaults to being in descending order (root ancestor first,
        immediate parent last); passing ``True`` for the ``ascending``
        argument will reverse the ordering (immediate parent first, root
        ancestor last).
        """
        if self.is_root_node():
            return None

        return TreeNode.all().filter("left_no < ",self.left_no).filter("right_no >",self.right_no).order_by('%sleft_no' % {True: '-', False: ''}[ascending])

    def get_children(self):
        """
        Creates a ``QuerySet`` containing the immediate children of this
        model instance, in tree order.

        The benefit of using this method over the reverse relation
        provided by the ORM to the instance's children is that a
        database query can be avoided in the case where the instance is
        a leaf node (it has no children).
        """
        if self.is_leaf_node():
            return None

        return TreeNode.all().filter('parent_node =',self.parent_node)

    def get_descendants(self, include_self=False):
        """
        Creates a ``QuerySet`` containing descendants of this model
        instance, in tree order.

        If ``include_self`` is ``True``, the ``QuerySet`` will also
        include this model instance.
        """
        if not include_self and self.is_leaf_node():
            return None
        if include_self:
            return self.get_subtree(self.left_no-1,self.right_no+1)
        else:
            return self.get_subtree(self.left_no,self.right_no)

    @classmethod
    def get_subtree(cls, left_no, right_no):
        """  Creates a ``QuerySet`` containing subtree nodes for the given left/right numbers """
        return cls.all().filter("left_no > ",left_no).filter("right_no <=",right_no-1).order('left_no')

    @classmethod
    def get_next_sibling(cls):
        """ Returns this model instance's next sibling in the tree, or ``None`` if it doesn't have a next sibling. """
        return cls.all().filter("left_no = ",self.right_no + 1).get()

    def get_previous_sibling(self):
        """ Returns this model instance's previous sibling in the tree, or ``None`` if it doesn't have a previous sibling. """
        return TreeNode.all().filter("right_no = ",self.left_no - 1).get()

    def get_root(self):
        """ Returns the root node of this model instance's tree. """
        if self.is_root_node():
            return self
        return TreeNode.all().filter("left_no < ",self.left_no).filter("right_no >",self.right_no).filter('parent_node =',None).get()

    @classmethod   
    def get_roots(cls):
        """ Returns the node without parents """
        return cls.all().filter("parent_node =",None)

    POSITIONS = ('first-child', 'last-child', 'left', 'right')

    def move_to(self, target, position='first-child'):
        """
        Moves ``node`` relative to a given ``target`` node as specified by ``position`` (when appropriate), by examining both nodes and
        calling the appropriate method to perform the move.

        A ``target`` of ``None`` indicates that ``node`` should be turned into a root node.

        Valid values for ``position`` are ``'first-child'``, ``'last-child'``, ``'left'`` or ``'right'``.

        ``node`` will be modified to reflect its new tree state in the database.
        """
        if TreeNode.POSITIONS[3] == position:
            delta_left      = self.right_no - self.left_no + 1
            delta_right     = target.right_no - self.right_no
            self.right_no   = target.right_no
            self.left_no    += delta_right
            descendants     = target.get_descendants().fetch(300,0)
            for n in descendants:
                n.left_no += delta_left
                n.right_no += delta_right
            target.right_no += delta_left
            self.parent_node = target.parent_node
            self.put()
            target.put()


    def insert_at(self, target, position=POSITIONS[0], commit=False):
        """
        Convenience method for calling ``TreeManager.insert_node`` with this
        model instance.
        """
        pass

    def insert_node(self, node, target, position='last-child', commit=False):
        """
        Sets up the tree state for ``node`` (which has not yet been
        inserted into in the database) so it will be positioned relative
        to a given ``target`` node as specified by ``position`` (when
        appropriate) it is inserted, with any neccessary space already
        having been made for it.

        A ``target`` of ``None`` indicates that ``node`` should be
        the last root node.

        If ``commit`` is ``True``, ``node``'s ``save()`` method will be
        called before it is returned.
        """
        pass

    def crate_space(self, left_no, right_no):
        """ Creates a space to insert or move nodes """
        to_move = self.get_subtree(left_no, righ_no).fetch(300,0)
        for n in to_move:
            n.left_no += 2
            n.right_no += 2
        ancestors = TreeNode.all().filter("left_no < ",left_no).filter("right_no >",right_no).fetch(300,0)
        for n in ancestors:
            n.rigth_no += 2
    