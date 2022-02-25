from random import randint


def generate_array(num) -> list:
    res = []
    for _ in range(num):
        lis = []
        for _ in range(num):
            lis.append(randint(10, 99))
        res.append(lis)
        del lis
    return res


def calc_diagonal(arr):
    diagonal_sum = 0
    diagonal_1_sum = 0
    len_arr = len(arr)
    for i in range(len_arr):
        diagonal_sum += arr[i][i]
        diagonal_1_sum += arr[i][len_arr - i -1]
    return {1: diagonal_sum / len_arr,
            2: diagonal_1_sum / len_arr}


def print_arrary(arr):
    for i in arr:
        for j in i:
            print(j, end='\t')
        print('\n')


arr = generate_array(5)
print_arrary(arr)
print(calc_diagonal(arr))