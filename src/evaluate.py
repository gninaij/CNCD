#!/usr/bin/python
#coding=utf8
"""
# Author: andy
# Created Time : 2025-08-18 16:45:05

# File Name: evaluate.py
# Description:

"""
import json

def eva_task1(result_file, sub_set='test'):
    if sub_set == 'test':
        label_file = '../dataset/test/CNCD.jsonl.task1.positive'
    elif sub_set == 'train':
        label_file = '../dataset/train/CNCD.jsonl.task1.positive'
    elif sub_set == 'valid':
        label_file = '../dataset/valid/CNCD.jsonl.task1.positive'
    else:
        print(f'sub_set is wrong, need "train", "valid" or "test", input parameter is {sub_set}')
    positive = set()
    with open(label_file) as fp:
        for line in fp:
            line = line.strip()
            news = json.loads(line)
            positive.add(news['id'])
    print(len(positive))
    results = []
    right_cnt = 0
    with open(result_file) as fp:
        for line in fp:
            line = line.strip()
            news = json.loads(line)
            results.append(news['id'])
            if news['id'] in positive:
                right_cnt += 1
    precision = right_cnt/len(results)
    print(f'precision:{precision}')
    recall = right_cnt/len(positive)
    print(f'recall:{recall}')
    f1 = 2 * precision * recall / (precision + recall)
    print(f'f1-score:{f1}')


def eva_task2(result_file, sub_set='test'):
    if sub_set == 'test':
        task2_label_file = '../dataset/test/CNCD.jsonl.task2.CRP'
    elif sub_set == 'train':
        task2_label_file = '../dataset/train/CNCD.jsonl.task2.CRP'
    elif sub_set == 'valid':
        task2_label_file = '../dataset/valid/CNCD.jsonl.task2.CRP'
    else:
        print(f'sub_set is wrong, need "train", "valid" or "test", input parameter is {sub_set}')
    positive = set()
    with open(task2_label_file) as fp:
        for line in fp:
            line = line.strip()
            pair = eval(line)
            positive.add(pair)
    results = []
    right_cnt = 0
    with open(result_file) as fp:
        for line in fp:
            line = line.strip()
            pair = eval(line)
            results.append(pair)
            if pair in positive:
                right_cnt += 1
    precision = right_cnt/len(results)
    print(f'right:{right_cnt}')
    print(f'precision:{precision}')
    recall = right_cnt/len(positive)
    print(f'recall:{recall}')
    f1 = 2 * precision * recall / (precision + recall)
    print(f'f1-score:{f1}')


if __name__ == '__main__':
    #  task1
    result_file = '../dataset/test/CNCD.jsonl.task1.pred'
    print(f'task1 test {result_file}')
    eva_task1(result_file, 'test')

    #  task2
    result_file = '../dataset/test/CNCD.jsonl.task2.pred_llm'
    print(f'task2 test {result_file}')
    eva_task2(result_file, 'test')

