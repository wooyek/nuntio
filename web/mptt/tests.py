import logging
import datetime
import unittest
logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(levelname)-7s %(module)s.%(funcName)s - %(message)s')

from google.appengine.ext import db

import django.contrib.auth.models

from  models import *

class Node(TreeNode):
    name = db.StringProperty()

def printTree():
    print '### Tree ###'
    roots = Node.get_roots().fetch(300,0)
    printNodes(roots,0)

def printNodes(nodes, indent):
    pre = indent * ' '
    for n in nodes:
        print pre + ("%s = [%d, %d]" % (n.name, n.left_no, n.right_no))
        printNodes(n.children_set, indent+4)


class MoveNodes(unittest.TestCase):
    def setUp(self):
        a = Node(name='A', left_no= 1, right_no=22)
        a.put()
        b = Node(name='B', left_no= 2, right_no=11, parent_node=a)
        b.put()
        c = Node(name='C', left_no= 3, right_no= 6, parent_node=b)
        c.put()
        d = Node(name='D', left_no= 4, right_no= 5, parent_node=c)
        d.put()
        e = Node(name='E', left_no= 7, right_no=10, parent_node=b)
        e.put()
        f = Node(name='F', left_no= 8, right_no= 9, parent_node=e)
        f.put()
        g = Node(name='G', left_no=12, right_no=21, parent_node=a)
        g.put()
        h = Node(name='H', left_no=13, right_no=16, parent_node=g)
        h.put()
        i = Node(name='I', left_no=14, right_no=15, parent_node=h)
        i.put()
        j = Node(name='J', left_no=17, right_no=20, parent_node=g)
        j.put()
        k = Node(name='K', left_no=18, right_no=19, parent_node=j)
        k.put()
        printTree()

    def testMoveLeaf(self):
        pass
        d = Node.all().filter('left_no =', 4).get()
        b = Node.all().filter('left_no =', 2).get()
        d.move_to(b, TreeNode.POSITIONS[3])
        printTree()
