from concurrent.futures import Executor, ThreadPoolExecutor
import argparse
import json
import urllib3

http = urllib3.PoolManager()
url = 'https://imaginglaboratory.azurewebsites.net/api/GetData'
code = 'ac8poJAuASe0OFoiTKwH8ZRWUDUGQTXa9KC3HQZHWJGUhb4h0hqrWw=='

parser = argparse.ArgumentParser()
parser.add_argument('-input')
parser.add_argument('-workers', type=int)
args = vars(parser.parse_args())

def zeros_matrix(size):
    M = [[0]*size for i in range(size)]
    return M

def matrix_sum(a, b):
    result = zeros_matrix(len(a))
    for i in range(len(a)):
        for j in range(len(b[0])):
            result[i][j] = a[i][j] + b[i][j]
    return result

def matrix_sub(a, b):
    result = zeros_matrix(len(a))
    for i in range(len(a)):
        for j in range(len(b[0])):
            result[i][j] = a[i][j] - b[i][j]
    return result

def matrix_mult(a, b):
    result = zeros_matrix(len(a))
    for i in range(len(a)):
        for j in range(len(b[0])):
            for k in range(len(b)):
                result[i][j] += a[i][k] * b[k][j]
    return result

matrix_operations = {
    'add': matrix_sum,
    'subtraction': matrix_sub,
    'multiplication': matrix_mult,
}

def execute_web_request(size):
    r = http.request('GET', url + '?code=' + code + '&size=' + size)
    return json.loads(r.data)

def calculate_result_and_save_into_tsv(data):
    result = matrix_operations[data['operation']](data['imageA'], data['imageB'])
    np.savetxt(data['fileName'], result, fmt="%d", delimiter="\t")

if __name__ == '__main__':
    sizes = [row.strip() for row in open(args['input'], 'r').readlines()]
    with ThreadPoolExecutor(max_workers=args['workers']) as executor:
        web_request_results = executor.map(execute_web_request, sizes)
    [calculate_result_and_save_into_tsv(data) for data in web_request_results]
