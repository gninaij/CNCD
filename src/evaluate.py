#!/usr/bin/python
#coding=utf8
"""
# Author: andy
# Created Time : 2025-08-18 16:45:05

# File Name: evaluate.py
# Description:

"""
import json, ast

def eva_task1(result_file):
    label_file = '../dataset/CNCD.task1.positive.jsonl'
    positive = set()
    with open(label_file) as fp:
        for line in fp:
            line = line.strip()
            news = json.loads(line)
            positive.add(news['id'])
    print(f'positive count: {len(positive)}')
    results = []
    right_cnt = 0
    with open(result_file) as fp:
        for line in fp:
            line = line.strip()
            news = json.loads(line)
            results.append(news['id'])
            if news['id'] in positive:
                right_cnt += 1
    if results:
        precision = right_cnt/len(results)
    else:
        precision = 0
    print(f'precision:{precision}')
    if positive:
        recall = right_cnt/len(positive)
    else:
        recall = 0
    print(f'recall:{recall}')
    if precision > 0 or recall > 0:
    	f1 = 2 * precision * recall / (precision + recall)
    else:
        f1 = 0
	print(f'f1-score:{f1}')


def eva_task2(result_file):
    task2_label_file = '../dataset/CNCD.task2.CRP'
    positive = set()
    with open(task2_label_file) as fp:
        for line in fp:
            line = line.strip()
            pair = ast.literal_eval(line)
            positive.add(pair)
    results = []
    right_cnt = 0
    with open(result_file) as fp:
        for line in fp:
            line = line.strip()
            pair = ast.literal_eval(line)
            results.append(pair)
            if pair in positive:
                right_cnt += 1
    if results:
        precision = right_cnt/len(results)
    else:
        precision = 0
    print(f'right:{right_cnt}')
    print(f'precision:{precision}')
    if positive:
        recall = right_cnt/len(positive)
    else:
        recall = 0
    print(f'recall:{recall}')
    if precision > 0 or recall > 0:
    	f1 = 2 * precision * recall / (precision + recall)
    else:
        f1 = 0
	print(f'f1-score:{f1}')


if __name__ == '__main__':
    #  task1
    result_file = '../output/task1.pred'
    print(f'task1 {result_file}')
    eva_task1(result_file)

    #  task2
    result_file = '../output/task2.pred_llm'
	#  result_file = '../output/task2.pred_ent_sim_llm'
	#  result_file = '../output/task2.pred_ent_llm'
	#  result_file = '../output/task2.pred_sim_llm'
    print(f'task2 {result_file}')
    eva_task2(result_file)

