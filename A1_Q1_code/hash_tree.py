#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : Cai Zhao
# python version 3.6.5
# using pep8 pycodestyle

import csv
import re


def load_candiate_item_sets(filename):
    """
    supporse put candidate item sets of length 3
    in the file candiate_item_sets.csv
    this function loads the sets in a list
    :param filename:
    :return:sets list
    """
    reader = csv.reader(open(filename, 'r'), delimiter=',')
    sets_list = []

    for row in reader:
        for i in range(len(row)):
            #  exact number chars to a list
            tmp_list = re.findall(r"\d+\.?\d*", row[i])
            # change chars in list to numbers
            tmp_list = [int(i) for i in tmp_list]
            #  print(tmp_list)
            sets_list.append(tmp_list)
    #  print(sets_list)
    return sets_list


class HashNode:

    def __init__(self):
        self.children = {}
        self.bucket = {}
        self.isLeaf = True
        self.depth = 0


class HashTree:

    def __init__(self, max_leaf_size, max_child_size):
        self.root = HashNode()
        self.max_leaf_size = max_leaf_size
        self.max_child_size = max_child_size

    def recursive_insert_nodes(self, itemset, node, depth, count):
        """
        Recursively insert nodes inside the tree
        and if required splits leaf node and
        redistributes itemsets among child converting itself
        into intermediate node.
        :param itemset:
        :param node:
        :param depth:
        :param count: can record time of the itemset appeared
        """
        node.depth = depth

        if depth == len(itemset):
            # last bucket  just insert
            if itemset in node.bucket:
                node.bucket[itemset] += count
            else:
                node.bucket[itemset] = count
            return
        if node.isLeaf:
            if itemset in node.bucket:
                node.bucket[itemset] += count
            else:
                node.bucket[itemset] = count
            if len(node.bucket) > self.max_leaf_size:
                # if bucket stores more itemsets than the max_leaf_size,
                # split the node as required
                # and the hash value will be computed for the spliting
                for old_itemset, old_count in node.bucket.items():
                    hash_key = self.hash(old_itemset[depth])
                    if hash_key not in node.children:
                        #  spliting the node
                        node.children[hash_key] = HashNode()
                    # the depth increases 1
                    self.recursive_insert_nodes(
                        old_itemset,
                        node.children[hash_key],
                        depth + 1, old_count)

                node.isLeaf = False
                #  only leaf node store itemsets,
                #  this node is not a leaf node any more
                del node.bucket
        else:
            hash_key = self.hash(itemset[depth])
            if hash_key not in node.children:
                node.children[hash_key] = HashNode()
            self.recursive_insert_nodes(
                itemset,
                node.children[hash_key],
                depth + 1, count)

    def insert_items(self, itemset):
        # list can't be hashed
        # convert the type into tuple can be easily hashed in leaf node buckets
        itemset = tuple(itemset)
        self.recursive_insert_nodes(itemset, self.root, 0, 1)

    def dfs_order_by_hash(self, node):
        """
        dfs trevsering the hash tree
        print the leaf node depth and list_items
        :param node:
        :return:
        """
        if node.isLeaf:
            list_items = list(node.bucket.keys())
            print('leaf node itemsets: ', list_items)
            print('leaf node depth: ', node.depth)
            #  print('leaf node bucket :', node.bucket)
            return
        #  order by hash value
        if 1 in node.children:
            self.dfs_order_by_hash(node.children.get(1))
        if 2 in node.children:
            self.dfs_order_by_hash(node.children.get(2))
        if 0 in node.children:
            self.dfs_order_by_hash(node.children.get(0))

    def hash(self, val):
        return val % self.max_child_size


def generate_hash_tree(candidate_itemsets, max_leaf_size=3, max_child_size=3):
    """
    generates hash tree of itemsets
    with each node having no more than max_child_size
    childs and each leaf node having no more than
    max_leaf_size candidate_itemset.
    """
    hash_tree = HashTree(max_child_size, max_leaf_size)
    for itemset in candidate_itemsets:
        # add this itemset to hashtree
        hash_tree.insert_items(itemset)
    return hash_tree


candidate_item_sets = load_candiate_item_sets('candiate_item_sets.csv')
hash_tree = generate_hash_tree(candidate_item_sets, 3, 3)
#  print leaf node itemsets and depth
hash_tree.dfs_order_by_hash(hash_tree.root)
