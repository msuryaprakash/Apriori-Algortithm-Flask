
import os
from itertools import chain, combinations
from collections import defaultdict
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import datetime

application = Flask(__name__)

application.config["UPLOAD_FOLDER"] = "static/"


def subsets(arr):
    return chain(*[combinations(arr, i + 1) for i, a in enumerate(arr)])


def min_support_items(item_set, transaction_list, min_support, freq_set):
    _item_set = set()
    local_set = defaultdict(int)

    for item in item_set:
        for transaction in transaction_list:
            if item.issubset(transaction):
                freq_set[item] += 1
                local_set[item] += 1

    for item, count in local_set.items():
        if count >= min_support:
            _item_set.add(item)
    return _item_set


def combine_set(item_set, length):
    return set(
        [i.union(j) for i in item_set for j in item_set if len(i.union(j)) == length]
    )


def find_frequency_1_dataset(iterator):
    transaction_list = list()
    item_set = set()
    for record in iterator:
        transaction = frozenset(record)
        transaction_list.append(transaction)
        for item in transaction:
            item_set.add(frozenset([item]))  # Generate 1-item_sets
    return item_set, transaction_list


def run_apriori(data_iter, min_support):
    item_set, transaction_list = find_frequency_1_dataset(data_iter)
    freq_set = defaultdict(int)
    large_set = dict()
    onec_set = min_support_items(item_set, transaction_list, min_support, freq_set)
    currentl_set = onec_set
    k = 2
    while currentl_set != set([]):
        large_set[k - 1] = currentl_set
        currentl_set = combine_set(currentl_set, k)
        current_set = min_support_items(
            currentl_set, transaction_list, min_support, freq_set
        )
        currentl_set = current_set
        k = k + 1

    frequent_items = []
    if not large_set:
        return []
    length = 1
    while length<len(large_set):
        for item in large_set.get(length):
            is_superset_frequent = False
            for superset in large_set.get(length+1):
                if frozenset.issubset(item, superset):
                    is_superset_frequent = True
            if not is_superset_frequent:
                frequent_items.append((tuple(item), freq_set[item]))
        length = length+1
    for item in large_set.get(length):
        frequent_items.append((tuple(item), freq_set[item]))
    return frequent_items

def format_results(items):
    i = []
    for item, count in sorted(items, key=lambda x: x[1]):
        i.append(item)
    return set(i)


def get_data(fname):
    with open(fname, newline="") as file_iter:
        for line in file_iter:
            line = line.strip().rstrip(",")  
            record = frozenset(list(map(str.strip, line.split(",")[1:])))
            yield record

@application.route('/')
def upload_file():
    return render_template('index.html')

#Result page.
@application.route('/display', methods = ['GET', 'POST'])
def save_file():
    if request.method == 'POST':
        f = request.files['file']
        s = request.form['support']
        support =int(s)
        filename = secure_filename(f.filename)

        basedir = os.path.abspath(os.path.dirname(__file__))

        f.save(os.path.join(basedir, application.config['UPLOAD_FOLDER'], filename))
        file = open(application.config['UPLOAD_FOLDER'] + filename,"r")
        content = file.read()
        
      
        inFile = []
    for line in content.split('\n'):
        line = line.strip().rstrip(",")  # Remove trailing comma
        record = frozenset(list(map(str.strip, line.split(",")[1:]))) 
        inFile.append(record)
    
    if inFile is not None:  
        start = datetime.datetime.now()
        items = run_apriori(inFile, support)
        #print(items)
        
        #calculating the algorithm execution time
        end = datetime.datetime.now()
        program_run_time = str((end - start))  

        res= format_results(items)
        total_item = len(items)  
        

    return render_template('content.html', res=res ,items =items ,s=s,total_item = total_item ,filename =filename , content= content, program_run_time =program_run_time) 




if __name__ == '__main__':
    application.run()