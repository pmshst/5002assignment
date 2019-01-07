#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : Cai Zhao
# python version 3.6.5
# using pep8 pycodestyle

import csv


def clean_data(filename):
    """
    clean data in the file
    remove invalid delimiter=','
    :param filename:
    :return: a new file clean.csv
    """
    original_file = open(filename)
    clean_file = open("clean.csv", "w")
    while 1:
        line = str(original_file.readline())
        offerset = int(line.find(',,'))
        if offerset != -1:
            clean_file.write(line[0:offerset]+'\n')
        else:
            clean_file.write(line)
        if not line:
            break
    original_file.close()
    clean_file.close()


def load_transactions(filename):
    """
    load transactions from cleaned data file
    :param filename:
    :return: a dictionary of transactions
    """
    reader = csv.reader(open(filename, 'r'), delimiter=',')
    transactions = {}
    for row in reader:
        tran = frozenset(row)
        transactions[tran] = transactions.get(tran, 0) + 1
    return transactions


class FPtreeNode:
    def __init__(self, item, count, parent):
        """

        :param item:
        :param count:
        :param parent:
        """
        self.item = item
        self.count = count
        # link the nodes with same item
        self.link = None
        # record the parent node
        self.parent = parent
        self.children = {}
        # for print the tree in nested list
        self.ready_flag = False
        self.sub_tree = []

    def increase(self, count):
        """
        increase the count of the node
        :param count:
        :return:
        """
        self.count += count

    def print_fp_tree(self, incedent=1):
        """
        just for degbug and check
        :param incedent:
        :return:
        """
        print('   ' * incedent, self.item, ' ', self.count)
        for child in self.children.values():
            child.print_fp_tree(incedent + 1)

    def get_fp_tree_height(self):
        """
        get condtional fptree's height
        for print it when the height is larger than 2
        :return:
        """
        if(len(self.children) == 0):
            return 0
        else:
            height = []
        for child in self.children.values():
            height.append(child.get_fp_tree_height())
            height.sort()
        return height[-1]+1

    def set_tree_leaf_nodes(self):
        """
        set the subtree of leaf nodes in fptree
        set the subtree and ready_flag
        :return:
            """
        nodes = []
        stack = [self]
        while stack:
            cur_node = stack[0]
            stack = stack[1:]
            if (len(cur_node.children.values()) == 0):
                nodes.append(cur_node)
                string = str(cur_node.item) + ' ' + str(cur_node.count)
                cur_node.sub_tree.append(string)
                cur_node.ready_flag = True
            for child in cur_node.children.values():
                stack.insert(0, child)
        return nodes

    def get_fp_tree_nested_list(self):
        """
        print fp tree_nested_list accoding the question
        traversing the tree
        when a parent node'children are ready to generate
        the parent's subtree, then generate it
        until the root has its subtree
        """
        while (self.ready_flag is False):
            stack = [self]
            while stack:
                cur_node = stack[0]
                stack = stack[1:]
                # all the chilren be readly to
                # compute the parent's sub_tree in con fp_tree
                flag = True
                for child in cur_node.children.values():
                    flag = child.ready_flag and flag
                #  all the chilren be readly
                #   generat sub tree
                if (flag is True):
                    cur_node.ready_flag = True
                    string = str(cur_node.item) + ' ' + str(cur_node.count)
                    cur_node.sub_tree.append(string)
                    children_num = len(cur_node.children.values())
                    tmp = []
                    for child in cur_node.children.values():
                        # Only on one child append a list
                        if (children_num == 1):
                            cur_node.sub_tree.append(child.sub_tree)
                            break
                        # several children put the element to a new list
                        else:
                            # leaf node Only one element in its subtree
                            if len(child.children.values()) == 0:
                                tmp.append(child.sub_tree[0])
                            else:
                                tmp.append(child.sub_tree)
                    # append all children's sub_tree to
                    # the parent's subtree
                    if (children_num > 1):
                        cur_node.sub_tree.append(tmp)
                else:
                    for child in cur_node.children.values():
                        if (child.ready_flag is False):
                            stack.insert(0, child)
        print(self.sub_tree)
        return self.sub_tree


def create_fptree(tran_dic, support_threshold=1):
    """
    create fp tree
    :param tran_dic:
    :param support_threshold:
    :return:
    """
    header_table = {}
    # count the item
    for tran in tran_dic:
        for item in tran:
            # tran_dic[tran] is the frequency of tran
            header_table[item] = header_table.get(item, 0) + tran_dic[tran]
    for item in list(header_table):
        # remove the non-freqent patterns
        # reduce the complexity
        if header_table[item] < support_threshold:
            del (header_table[item])
    freq_item_set = set(header_table.keys())
    # no need to create a fp_tree if there is no frequent item
    if len(freq_item_set) == 0:
        return None, None
    for item in header_table:
        # save support and node
        header_table[item] = [header_table[item], None]
        tree_root = FPtreeNode('Null Set', 1, None)
    for tran, count in tran_dic.items():
        tmp = {}
        for item in tran:
            if item in freq_item_set:
                tmp[item] = header_table[item][0]
        if len(tmp) > 0:
            # ordered reversely by the support
            ordered_items = [item[0] for item in sorted(
                tmp.items(),
                key=lambda k: k[1],
                reverse=True)]
            update_fptree(ordered_items, tree_root, header_table, count)
    return tree_root, header_table


def update_fptree(items, node, headerTable, count):
    """
    update fp tree recursively
    :param items: ordered item
    :param node:
    :param headerTable:
    :param count:
    :return:
    """
    if items[0] in node.children:
        node.children[items[0]].increase(count)
    else:
        node.children[items[0]] = FPtreeNode(items[0], count, node)
        if headerTable[items[0]][1] is None:
            headerTable[items[0]][1] = node.children[items[0]]
        else:
            update_header_link(
                headerTable[items[0]][1],
                node.children[items[0]])
    if len(items) > 1:
        update_fptree(items[1:], node.children[items[0]], headerTable, count)


def update_header_link(start, end):
    """
    update link relationship within tree nodes
    :param start:
    :param end:
    :return:
    """
    while (start.link is not None):
        start = start.link
    start.link = end


def generate_path(node, prefix_path):
    """
    trace from one of the linked nodes to the root
    recusively
    :param node:
    :param prefix_path:
    :return:
    """
    if node.parent is not None:
        prefix_path.append(node.item)
        generate_path(node.parent, prefix_path)


def find_prefix_paths(item, node):
    """
    find prefix paths in fp tree
    as the input of conditional fp tree
    :param item:
    :param node:
    :return:
    """
    con_input = {}
    while node is not None:
        prefixPath = []
        # trace to the root
        generate_path(node, prefixPath)
        if len(prefixPath) > 1:
            # create con-fptree input
            con_input[frozenset(prefixPath[1:])] = node.count
        node = node.link
    return con_input


def find_fp_in_tree(inTree, header_table, support_threshold, prefix, fp_list):
    """
    find frequent patterns in the tree recursively
    :param inTree:
    :param header_table:
    :param minSup:
    :param prefix:
    :param fp_list:
    :return:
    """
    #  sorted reversely by the support
    items = [item[0] for item in sorted(
        header_table.items(),
        key=lambda k: str(k[1]),
        reverse=True)]
    for item in items:
        # add to frequent item set
        new_fre_pattern = prefix.copy()
        new_fre_pattern.add(item)
        fp_list.append(new_fre_pattern)
        # create condtional fptree input
        cond_fp_input = find_prefix_paths(item, header_table[item][1])
        # create conditonal fptree
        con_tree_root, con_header_table = create_fptree(
            cond_fp_input,
            support_threshold)
        # recursively call and the exit
        if con_header_table is not None:
            height = con_tree_root.get_fp_tree_height()
            if(height > 1):
                con_tree_root.set_tree_leaf_nodes()
                con_tree_root.get_fp_tree_nested_list()
            find_fp_in_tree(
                con_tree_root,
                con_header_table,
                support_threshold,
                new_fre_pattern,
                fp_list)


def mine_frequent_patterns(tran_dic, support_threshold=300):
    """
    create the first fp tree and find frequent patterns
    in the tree
    :param tran_dic:
    :param support_threshold:
    :return:
    """
    fp_tree_root, head_table = create_fptree(tran_dic, support_threshold)
    freq_items = []
    find_fp_in_tree(
        fp_tree_root,
        head_table,
        support_threshold,
        set([]),
        freq_items)
    return freq_items


# clean original data generate clean.csv
clean_data('groceries.csv')
# load cleaned data clean.csv
tran_dic = load_transactions('clean.csv')
frequent_patterns = mine_frequent_patterns(tran_dic, 300)
fp_file = open("frequent_patterns.csv", "w")
for pattern in frequent_patterns:
    fp_file.writelines('\"' + str(pattern) + '\"\n')
fp_file.close()
