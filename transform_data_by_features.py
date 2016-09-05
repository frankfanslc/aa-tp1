import pandas as pd
import re
import multiprocessing
import collections
from load_development_dataset import df 


def generate_content_types(row):
    email = row['email']
    output = collections.defaultdict(bool)
    check = ['x-world', 'application', 'text', 'text/plain', 'text/html', 'video', 'audio', 'image', 'drawing', 'model', 'multipart', 'x-conference', 'i-world', 'music', 'message', 'x-music', 'www', 'chemical', 'paleovu', 'windows', 'xgl']
    
    for part in row['email'].walk():
        ct = part.get_content_type()
        
        for kind in check:
            output['has_' + kind] |= ct.startswith(kind)
    
    return output

def generate_number_of_spaces(row):
    email = str(row['email'])
    
    return {
        'spaces': email.count(' '),
        'newlines': email.count('\n')
    }

def number_of_images(row):
    email = row['email']
    output = { 'multipart_number': 0, 'number_of_images': 0 }
    rgx = re.compile('\.(jpeg|jpg|png|gif|bmp)')
    
    for part in email.walk():
        output['multipart_number'] += 1
        
        if part.get_content_type().startswith('image/'):
            output['number_of_images'] += 1
        elif part.get_content_type() == 'text/html' or part.get_content_type() == 'text/plain':
            output['number_of_images'] += len(re.findall(rgx, part.get_payload()))
    
    return output

# Functions which create the output features
transforms = [
    lambda row: {'class': row['class']},
    lambda row: {'length': len(row['email'])},
    #generate_multipart_number,
    generate_content_types,
    generate_number_of_spaces,
    number_of_images]

# Set up thread pool
def transform_row(x):
    (index, row) = x
    current = {}
    
    for function in transforms:
        current.update(function(row))
    
    return current

print("Processing")
pool = multiprocessing.Pool(2)

# Create dataframe
transformed = pool.map(transform_row, df.iterrows())

print("Done!")

try:
    del ds
except:
    pass

ds = pd.DataFrame(transformed)