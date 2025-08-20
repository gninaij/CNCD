# CNCD

Chinese News Contradiction Dataset

## Dataset Description

CNCD is a dataset designed for detecting contradictions in news articles. The data is located in the "dataset" directory. The label distribution is shown in the following table:

<style>
</style>

| **Label Type**                                           | **Train** | **Valid** | **Test** | **Total** |
| -------------------------------------------------------- | --------- | --------- | -------- | --------- |
| **Denial Reports**                                       | 534       | 270       | 1153     | 1957      |
| **Denial Reports with corresponding Denied<br> Reports** | 182       | 96        | 322      | 600       |
| **Denied Reports**                                       | 204       | 162       | 434      | 800       |
| **Conflicting Report Pairs**                             | 835       | 1280      | 2907     | 5022      |

## Baseline Method Description

### Environment Preparation

The code for this project was developed under Python 3.12.

#### Installing Dependencies

```shell
pip install -i requirements.txt
```

note: If you want to use a GPU, you need to replace the corresponding software packages in the requirements with their GPU versions.

#### Text Embedding Model

Download the BGE-3 model from the following URL:

https://huggingface.co/BAAI/bge-base-zh-v1.5/tree/main

Place the model files in the directory: model/BAAI/bge-base-zh-v1.5.

#### About ElasticSearch

Install Elasticsearch, with version 7.6.1 having been tested and confirmed to work. The specific installation process is omitted here.

When running the task for the first time, it is necessary to first create an index and add data in Elasticsearch.

Start ES on your system first.

code file：src/es_util.py

Use `create_index()` to establish an index.

Use `add_data2es_txt()` to add data.

Note: The data from the training set, validation set, and test set should not be used simultaneously on Elasticsearch . When switching tasks, all existing data should be deleted before adding the data from the target set. To delete all data, use `esWorker.delete_all()`.

#### About Faiss

When running the task for the first time, it is necessary to first create an index and add data in Faiss.

code file：src/faiss_util.py

Use `add_data2es_txt()` to add data from the target set into Faiss.

Note: The data from the training set, validation set, and test set should not be used simultaneously in Faiss. When switching tasks, all existing data should be deleted before adding data from the target set. To delete all data, use `faissWorker.delete_all()`.

Since text embedding is involved, adding data can be time-consuming.

## Run the task

Start ES on your system first.

#### Task1

code file：src/check_fake_task1.py

Here, you can select which data subset to process. The possible values for `sub_set` are 'test', 'train' or'valid'.

```python
if __name__ == '__main__':
    run(sub_set='test')
```

output file:

```python
out_file = f'{news_file}.task1.pred'
```

Run `run()` and wait for it to complete.

```python
if __name__ == '__main__':
    run(sub_set='test')
```

evaluation:

code file：src/evaluate.py

```python
#  task1    
result_file = '../dataset/test/CNCD.jsonl.task1.pred'    
print(f'train {result_file}')    
eva_task1(result_file, 'test')
```

#### Task2

code file：src/check_fake_task2.py

Configure which filters to use and which data subset to compute.

```python
if __name__ == '__main__':    
    #  whether use ENT FILTER
    USE_ENT_FILTER = False   
    #  whether use SIM FILTER 
    USE_SIM_FILTER = False    
    run(sub_set='test')
```

output file:

```python
    if USE_ENT_FILTER and USE_SIM_FILTER:                                                                             
        out_file = f'../dataset/{sub_set}/CNCD.jsonl.task2.pred_ent_sim_llm'                                          
    elif USE_ENT_FILTER and not USE_SIM_FILTER:                                                                                               
        out_file = f'../dataset/{sub_set}/CNCD.jsonl.task2.pred_ent_llm'                                                                                    
    elif not USE_ENT_FILTER and USE_SIM_FILTER:                                                                                                   
        out_file = f'../dataset/{sub_set}/CNCD.jsonl.task2.pred_sim_llm'                                                                                                
    else:                                                                                                                                                     
        out_file = f'../dataset/{sub_set}/CNCD.jsonl.task2.pred_llm' 
```

Run `run()` and wait for it to complete.

```python
    run(sub_set='test')
```

evaluation：

code file：src/evaluate.py

```python
#  task2    
result_file = '../dataset/test/CNCD.jsonl.task2.pred'    
print(result_file)    
eva_task2(result_file, 'test')
```