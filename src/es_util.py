import re
import json
import xlrd
from elasticsearch import Elasticsearch
from elasticsearch import helpers


class esWorker():
    def __init__(self, url="http://127.0.0.1:9200", index='news'):
        self.es = Elasticsearch([url])
        count_result = self.es.count(index="news")
        print(f"文档总数: {count_result['count']}")
        mapping = self.es.indices.get_mapping(index=index)
        print(mapping)


    def insert_data(self, datas):
        # input是json格式的
        # [{'id':新闻id, 'title':title, 'content':content, 'pubDate':'yyyy-mm-dd'}]
        actions = []
        for data in datas:
            actions.append({'_index':'news', '_id':data['id'], '_source':data})
            # self.es.index(index="news", id=data['id'], body=data)
        success_count, errors = helpers.bulk(self.es, actions)
        print(f"成功插入 {success_count} 条，失败 {len(errors)} 条")
        return


    def search_data(self, query, ents):
        es_query = {
            "from": 0,
            "size": 100,
            "query": {
                "bool": {
                    "must": [
                    ],
                    "should": [
                        {"match": {"content": query}}
                    ],
                    "minimum_should_match": 1
                }
            }
        }
        response = self.es.search(index='news', body=es_query)
        results = []
        for news in response['hits']['hits']:
            results.append({'id':news['_source']['id'], 'title':news['_source']['title'], 'content':news['_source']['content'], 'date':news['_source']['pubDate'], 'score':news['_score']})
        return results


    def delete_data(self, news_ids):
        for id in news_ids:
            response = self.es.delete(
                index = "news",
                id = id
            )
            print(f"删除结果: {response['result']}")


    def delete_all(self):
        response = self.es.delete_by_query(
            index = "news",
            body = {"query": {"match_all": {}}}
        )
        print(f"已删除 {response['deleted']} 条文档")


def add_data2es_txt():
    es_worker = esWorker()
    input_file = '../dataset/CNCD.jsonl'
    datas = []
    with open(input_file, encoding='utf8') as fp:
        for line in fp:
            line = line.strip()
            news = json.loads(line)
            nid = news['id']
            title = news['title']
            content = news['content']
            dt = news['date']
            json_data = {'id':nid, 'title':title, 'content':content, 'pubDate':dt}
            datas.append(json_data)
    es_worker.insert_data(datas)
    print(f'insert {len(datas)}')


def test_search():
    es_worker = esWorker()
    query = '特斯拉叫停与比亚迪合作'
    ents = ['特斯拉', '比亚迪']
    fields = ["title", "content"]
    es_worker.search_data(query, ents)


def create_index():
    url="http://127.0.0.1:9200"
    es = Elasticsearch([url])
    es.indices.create(index="news",body={
        "mappings":{
            "properties":{
                'id': {'type': 'integer', 'index': False},
                'title': {'type': 'text', 'analyzer': 'ik_max_word'},
                'content': {'type': 'text', 'analyzer': 'ik_max_word'},
                'pubDate': {'type': 'date'},
                'pubTime': {'type': 'date'},
                'time': {'type': 'text', 'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}}
            }
        }
    })


if __name__ == '__main__':
    #  test_search()
    #  add_data2es_txt()
    create_index()
