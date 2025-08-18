import os, re
import json
import faiss
import pickle
import numpy as np

import text_util
import log_uti
logger = log_util.getLogger(__name__)


class faissWorker():
    def __init__(self, parameter):
        self.db_file = parameter['db_file']
        self.data_file = parameter['data_file']
        self.vec_size = 768 # from bge
        self.index, self.news_data = self.load_db(self.db_file, self.data_file)
        self.emb_model = parameter['emb_model']


    def load_db(self, db_file, data_file):
        if os.path.exists(db_file):
            with open(db_file, 'rb') as fp:
                index = pickle.load(fp)
            with open(data_file, 'rb') as fp:
                news_data = pickle.load(fp)
        else:
            index = faiss.index_factory(self.vec_size, 'IDMap,Flat', faiss.METRIC_INNER_PRODUCT)
            news_data = {}
        logger.info(f'index vec count:{index.ntotal}')
        logger.info(f'news count:{len(news_data)}')
        return index, news_data


    def add_news(self, news_list):
        batch_size = 128
        batch_input = []
        batch_ids = []
        for i, news in enumerate(news_list):
            head = text_util.get_head(news['title'], news['content'])
            batch_input.append(head)
            batch_ids.append(news['id'])
            self.news_data[news['id']] = news
            if len(batch_input) == batch_size or i == len(news_list) - 1:
                embeddings = self.emb_model.encode(batch_input)
                for k in range(0, embeddings.shape[0]):
                    vec = embeddings[k]
                    id = batch_ids[k]
                batch_ids = np.array(batch_ids, dtype=np.int64)
                self.index.add_with_ids(embeddings, batch_ids)
                batch_input = []
                batch_ids = []
                logger.info(f'embedding {i} news')
        with open(self.db_file, 'wb') as fp:
            pickle.dump(self.index, fp)
        with open(self.data_file, 'wb') as fp:
            pickle.dump(self.news_data, fp)


    def del_news(self, del_ids):
        self.index.remove_ids(np.array(del_ids, dtype=np.int64))
        for id in del_ids:
            if id in self.news_data:
                self.news_data.pop(id)


    def del_all(self):
        self.index.reset()
        self.news_data = {}


    def search_news(self, query, k=50):
        query_vecs = embeddings = self.emb_model.encode([query])
        sim_arr, idx_arr = self.index.search(query_vecs, k)
        results = []
        for i in range(0, sim_arr.shape[1]):
            id = idx_arr[0][i]
            if id < 0:
                break
            results.append({'sim':sim_arr[0][i], 'news':self.news_data[id]})
        return results


def test_add():
    conf = {}
    conf['db_file'] = '../model/index.pickle'
    conf['data_file'] = '../model/news.pickle'
    conf['emb_model'] = emb_model
    faiss_worker = faissWorker(conf)
    news_data = []
    with open('../dataset/CNCD.jsonl', encoding='utf8') as fp:
        for lid, line in enumerate(fp):
            line = line.strip()
            id, pub_time, title, content = line.split('\t')
            pub_date = pub_time[:10]
            news = {'id':int(id), 'pub_date':pub_date, 'title':title, 'content':content}
            news_data.append(news)
            if lid == 100:
                break
    faiss_worker.add_news(news_data)


def test_search():
    conf = {}
    conf['db_file'] = '../model/index.pickle'
    conf['data_file'] = '../model/news.pickle'
    conf['emb_model'] = emb_model
    faiss_worker = faissWorker(conf)
    with open('../dataset/CNCD.jsonl', encoding='utf8') as fp:
        for lid, line in enumerate(fp):
            line = line.strip()
            id, pub_time, title, content = line.split('\t')
            pub_date = pub_time[:10]
            results = faiss_worker.search_news(title, 10)
            for res in results:
                print(res)
            if lid == 10:
                break


def add_data2es_txt():
    conf = {}
    conf['db_file'] = '../model/index.pickle'
    conf['data_file'] = '../model/news.pickle'
    conf['emb_model'] = emb_model
    faiss_worker = faissWorker(conf)
    p_endl = re.compile('#&#')
    input_file = '../dataset/CNCD.jsonl'
    datas = []
    with open(input_file, encoding='utf8') as fp:
        for line in fp:
            line = line.strip()
            news = json.loads(line)
            nid = news['id']
            if nid in old_ids:
                continue
            news['content'] = p_endl.sub('\n', news['content'])
            datas.append(news)
    faiss_worker.add_news(datas)
    print(f'insert {len(datas)}')


if __name__ == '__main__':
    from FlagEmbedding import FlagAutoModel
    emb_model_path = '../model/BAAI/bge-base-zh-v1.5'
    emb_model = FlagAutoModel.from_finetuned(emb_model_path,
                                             query_instruction_for_retrieval="为这个句子生成表示以用于检索相关文章：",
                                             use_fp16=True)
    add_data2es_txt()
