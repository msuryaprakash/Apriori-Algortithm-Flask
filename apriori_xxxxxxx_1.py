"""
Description: Implementation of the Apriori algorithm
Usage: python3 apriori_xxxxxxx.py <dataset_filename>
"""

import sys
import operator
from optparse import OptionParser
import numpy as np
import pandas as pd
import apyori
from apyori import apriori


def load_data(filename):
    data = pd.read_csv(filename, sep=',', header=None, on_bad_lines='skip')
    data = data.dropna()
    return data.values.tolist()


def apriori_gen(data, k):
    C = []
    for l1 in data:
        for l2 in data:
            first_itemlist = str(l1[0]).split(",")
            second_itemlist = str(l2[0]).split(",")

            i = 0
            flag = True
            while i <= k - 2 - 1:
                print(k)
                if first_itemlist[i] != second_itemlist[i]:
                    flag = False
                    break
                i += 1

            if not first_itemlist[k - 1 - 1] < second_itemlist[k - 1 - 1]:
                flag = False

            if flag == True:
                c = sorted(set(first_itemlist) | set(second_itemlist))

                if has_infrequent_subset(list(c), data, k - 1):
                    C.append(",".join(list(c)))

    return C


def powersets(s, k):
    """
    Returns non-empty subsets of a set
    """
    x = len(s)
    powerset = []
    list = None
    for i in range(1, 1 << x):
        list = [s[j] for j in range(x) if (i & (1 << j))]
        if len(list) == k:
            powerset.append(list)

    return powerset


def has_infrequent_subset(c, data, k):
    """
    Returns items with infrequent subset
    """
    subsets = powersets(c, k)

    for subset in subsets:

        frequent_subset = False
        for item in data:
            if set(subset) == set(item[0]):
                frequent_subset = True
                break

        if frequent_subset == False:
            return False

    return True


def find_frequent_1_itemset(data, min_sup):
    itemset = {}

    for i in data:
        for j in i:
            if j in itemset:
                itemset[j] += 1
            else:
                itemset[j] = 1

    for item in itemset.copy():
        if itemset[item] < min_sup:
            itemset.pop(item, None)

    return sorted(itemset.items(), key=operator.itemgetter(0))


def main():
    # parse options
    parser = OptionParser()

    parser.add_option("-f", "--inputFile", dest="inputFile", help="CSV Filename", metavar="FILE")
    parser.add_option("-m", "--minSupport", dest="minSupport", help="Minimum Support", metavar="SUPPORT")

    (options, args) = parser.parse_args()

    if options.inputFile is None:
        print("No dataset filename specified, system with exit\n")
        sys.exit(1)

    if options.minSupport is None:
        print("No minimum support specified, system with exit\n")
        sys.exit(1)

    # print filename
    print("inputfile " + options.inputFile)
    print("min_sup " + options.minSupport)

    # load data
    data = load_data(options.inputFile)

    # generate frequent 1-itemset
    find_frequent_1_itemset(data, int(options.minSupport))

    # generate frequent k-itemset
    C = apriori_gen(data, int(options.minSupport))
    print(C)

    # generate association rules
    rules = apriori(data, min_support=float(options.minSupport), min_confidence=0.5)

    # print rules
    for rule in rules:
        print(rule)

    print("End - total items: " + str(len(data)))


if __name__ == '__main__':
    main()
