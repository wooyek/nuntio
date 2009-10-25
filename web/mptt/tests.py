import logging
import datetime
import unittest
logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(levelname)-7s %(module)s.%(funcName)s - %(message)s')

from google.appengine.ext import db

import django.contrib.auth.models

from  models import *

class Node(TreeNode):
    name = db.StringProperty()

def printTree(text = 'Tree'):
    print '### %s ###' % text
    roots = Node.get_roots().fetch(300,0)
    printNodes(roots,0)

def printNodes(nodes, indent):
    pre = indent * ' '
    for n in nodes:
        print pre + ("%s (%s)" % (n.name, n.ordinal))
        printNodes(n.get_children().fetch(300,0), indent+4)


class MoveNodes(unittest.TestCase):
    def setUp(self):
        for n in Node.all().fetch(300,0):
            n.delete()
        a = Node(name='A', ordinal= 1, right_no=22)
        a.put()
        b = Node(name='B', ordinal= 1, right_no=11, parent_node=a)
        b.put()
        c = Node(name='C', ordinal= 1, right_no= 6, parent_node=b)
        c.put()
        d = Node(name='D', ordinal= 1, right_no= 5, parent_node=c)
        d.put()
        e = Node(name='E', ordinal= 2, right_no=10, parent_node=b)
        e.put()
        f = Node(name='F', ordinal= 1, right_no= 9, parent_node=e)
        f.put()
        g = Node(name='G', ordinal= 2, right_no=21, parent_node=a)
        g.put()
        h = Node(name='H', ordinal= 1, right_no=16, parent_node=g)
        h.put()
        i = Node(name='I', ordinal= 1, right_no=15, parent_node=h)
        i.put()
        j = Node(name='J', ordinal= 2, right_no=20, parent_node=g)
        j.put()
        k = Node(name='K', ordinal= 1, right_no=19, parent_node=j)
        k.put()
        printTree('Setup')

    def testMoveLeaf(self):
        n = Node.all().filter('name =', 'D').get()
        b = Node.all().filter('name =', 'B').get()
        n.move_to(b, TreeNode.POSITIONS[3])
        printTree('testMoveLeaf')
        self.assertEquals(n.ordinal, 2)
        self.assertEquals(n.parent_node, b.parent_node)

    def testMoveSubtreeRight(self):
        n = Node.all().filter('name =', 'E').get()
        b = Node.all().filter('name =', 'B').get()
        n.move_to(b, TreeNode.POSITIONS[3])
        printTree('testMoveSubtreeRight')
        self.assertEquals(n.ordinal, 2)
        self.assertEquals(n.parent_node, b.parent_node)

    def testMoveSubtreeLeft(self):
        n = Node.all().filter('name =', 'C').get()
        b = Node.all().filter('name =', 'B').get()
        n.move_to(b, TreeNode.POSITIONS[2])
        printTree('testMoveSubtreeLeft')
        self.assertEquals(n.ordinal, 1)
        self.assertEquals(n.parent_node, b.parent_node)

    def testMoveSubtreeIntoLast(self):
        n = Node.all().filter('name =', 'C').get()
        t = Node.all().filter('name =', 'A').get()
        n.move_to(t, TreeNode.POSITIONS[1])
        printTree('testMoveSubtreeIntoLast')
        self.assertEquals(n.ordinal, 3)
        self.assertEquals(n.parent_node, t)

    def testMoveSubtreeIntoFirst(self):
        n = Node.all().filter('name =', 'C').get()
        t = Node.all().filter('name =', 'A').get()
        n.move_to(t, TreeNode.POSITIONS[0])
        printTree('testMoveSubtreeIntoFirst')
        self.assertEquals(n.ordinal, 1)
        self.assertEquals(n.parent_node, t)
