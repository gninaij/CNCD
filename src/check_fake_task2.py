# -*- coding: utf-8 -*-
# only for task2
import re, os, pickle
import json
import traceback
from FlagEmbedding import FlagAutoModel
import numpy as np

import llm_worker
import text_util
import log_util
from es_util import esWorker
from faiss_util import faissWorker

logger = common_log.getLogger(__name__)

p_split_answer = re.compile('[。\n\r]+')

common_log.debug(__name__, True)

class Worker():
    def __init__(self, parameter):
        conf = json.loads(parameter)
        data_path = conf['data_path']
        self.llm = llm_worker.LlmWorker(data_path, use_buffer=True)
        self.version = conf.get('version', '1.0')
        self.es = esWorker()
        emb_model_path = conf['emb_model_path']
        self.emb_model = FlagAutoModel.from_finetuned(emb_model_path,
                                                      query_instruction_for_retrieval="为这个句子生成表示以用于检索相关文章：",
                                                      use_fp16=True)
        conf = {}
        conf['db_file'] = '../model/index.pickle'
        conf['data_file'] = '../model/news.pickle'
        conf['emb_model'] = self.emb_model
        self.faiss = faissWorker(conf)


    def process(self, parameter):
        """
        input:{'title':title, 'content':content, 'time':'YYYY-mm-dd HH:MM:SS', 'id':id}
        """
        try:
            results = self.process0(parameter)
            return json.dumps({'message':results, 'stat':0, 'version':self.version})
        except:
            logger.error(traceback.format_exc())
            return json.dumps({'message': [], 'stat': 1, 'errorMessage':traceback.format_exc(), 'version': self.version})


    def process0(self, parameter):
        input_data = json.loads(parameter)
        title = input_data['title']
        content = input_data['content']
        nid = input_data['id']
        news_date = input_data['date']
        # extract deny claim via LLM
        neg_data = self.llm_get_neg(title, content)
        if not neg_data or not neg_data['has_rumor']:
            return []
        logger.debug(f'title:{title}')
        logger.debug('澄清数据：%s' % str(neg_data))
        results = []
        for data in neg_data['rumor']:
            ents = data['subject']
            nums = data['number']
            locs = data['location']
            rumor_content = str(data['rumor_content'])
            logger.debug('rumor_content:%s' % rumor_content)

            # ES search
            es_results = self.es.search_data(rumor_content, ents)

            # faiss search
            faiss_results = self.faiss.search_news(rumor_content)
            
            # 合并两个search的结果
            merged_news1 = self.merge_es_faiss(es_results, faiss_results)

            # 过滤晚于澄清新闻的新闻
            merged_news1_fil = self.date_filter(news_date, merged_news1)

            merged_news2 = []
            # 先排除否认新闻
            for news in merged_news1_fil:
                if self.pattern_match(news['title'], news['content']):
                    continue
                merged_news2.append(news)
            # 先以主体、时间、数字、地点做比较
            target_news = {'id':nid, 'title':title, 'content':content, 'ents':ents, 'nums':nums, 'locs':locs}
            if USE_ENT_FILTER:
                valid_news1 = self.item_filter(target_news, merged_news2)
                logger.debug('valid_news1:')
            #  for news in valid_news1:
                #  logger.debug(str(news))
            else:
                valid_news1 = merged_news2

            # 再以文本向量做相似度比较
            if USE_SIM_FILTER:
                logger.debug('valid_news2:')
                valid_news2, valid_sims = self.sim_filter(target_news, valid_news1)

                for k, news in enumerate(valid_news2):
                    logger.debug(f'{valid_sims[k]}, {str(news)}')
            else:
                valid_news2 = valid_news1

            # 再以大模型提问做比较
            valid_news3 = self.llm_filter(target_news, valid_news2, ents, locs)
            results = valid_news3
            logger.debug('valid_news3')
            for news in valid_news3:
                logger.debug(str(news))

        return results


    def llm_get_neg(self, title, content):
        message = [
            {"role": "system",
             "content": "你是一个擅长阅读理解新闻的专家。阅读给出的新闻内容并一步一步地思考，然后依次做如下回答：\n1.根据给出的新闻回答新闻的主要内容是否针对某些已经披露的事情进行了明确地否认，以“是”或“否”进行回答；\n2.被否认的事情是什么，仅使用原文的语句进行回答；3.和被否认的事情相关的主要主体、主要地点（如果没有提及则为空）和重要数据（仅输出数值）；"},
            {"role": "user",
             "content": "特斯拉要在沙特建厂？马斯克在线辟谣\n9月18日，《华尔街日报》援引知情人士的消息报道称，沙特阿拉伯正与美国电动汽车制造商特斯拉就在沙特建立制造工厂进行初步谈判。 报道称，沙特阿拉伯一直在向特斯拉抛出橄榄枝，试图用从刚果民主共和国等国购买特斯拉电动汽车所需的一定数量的金属和矿产的权利来吸引其到当地建厂。 据悉，沙特正在考虑的一项举措是向大宗商品交易商Trafigura提供融资，帮助其完成刚果的一个钴铜项目，该项目可能有助于为特斯拉的一家工厂提供供应。此前，在成本不断上升和钴价持续低迷的情况下，Trafigura正在评估其对刚果Mutoshi项目的选择。 沙特一直在努力使其经济摆脱对石油的依赖，除了尝试吸引特斯拉之外，该国主权财富基金还是美国电动汽车初创公司Lucid Group 的主要投资者。 针对上述报道，特斯拉首席执行官埃隆·马斯克在社交媒体平台X上发帖进行了否认，而沙特阿拉伯的公共投资基金（Public Investment fund）拒绝置评。 特斯拉目前在全球拥有6家工厂，并正在墨西哥北部新莱昂州建设第七家工厂。今年5月，马斯克曾表示，特斯拉可能会在今年年底前敲定下一个工厂的最终选址。今年8月，特斯拉表示有兴趣在印度建立一家生产低成本电动汽车的工厂。日前，外媒又报道称土耳其总统雷杰普·塔伊普·埃尔多安（Recep Tayyip Erdogan）在美国纽约与马斯克会面，并邀请特斯拉在土耳其设立工厂。9月18日，马斯克还在加州会见了以色列总理Benjamin Netanyahu。 特斯拉的目标是到2030年每年销售2000万辆汽车，较2022年的130万辆将翻数倍。"},
            {"role": "assistant",
             "content": "文中有涉及到对某些事情进行了明确地否认。\n被否认的事情是“沙特阿拉伯正与美国电动汽车制造商特斯拉就在沙特建立制造工厂进行初步谈判”。\n主要主体：特斯拉、沙特阿拉伯；主要地点：沙特；重要数据：未提及"},
            {"role": "user",
             "content": title + '\n' + content}
        ]
        answer1, usage = self.llm.api('', message=message)
        logger.info(f'answer1:{answer1}')
        answer_lines = answer1.split('\n')
        p_negtive = re.compile('1\. *否')
        if p_negtive.search(answer1):
            return {}

        message = [
            {"role": "system",
             "content": "将下面的文本整合为如下的json格式；{\"has_rumor\" : True/False, \"rumor\" : [{\"subject\":[被否认事情相关的主要主体], \"number\":[重要数据], \"location\":[主要地点], \"rumor_content\" : 否认的事情}]}。"},
            {"role": "user",
             "content": '1. 文中有涉及到对某些事情进行了明确地否认。  \n2. 被否认的事情是："该等公司为国美非重要附属公司，冻结该等公司股权不会对公司的财务状况和经营产生重大影响。"  \n3. 主要主体：国美零售控股有限公司；主要地点：空；重要数据：68.9亿元。'},
            {"role": "assistant",
             "content": '{\n  "has_rumor": true,\n  "rumor": [\n    {\n      "subject": ["国美零售控股有限公司"],\n      "number": [68.9亿],\n      "location": [],\n      "rumor_content": "该等公司为国美非重要附属公司，冻结该等公司股权不会对公司的财务状况和经营产生重大影响。"\n    }\n  ]\n}'},
            {"role": "user",
             "content": answer1}
        ]
        answer2, usage = self.llm.api('', message=message)
        logger.info(f'answer2:{answer2}')
        answer_json = self.llm.get_json(answer2, use_llm=True)
        if not answer_json:
            return {}
        return answer_json


    def merge_es_faiss(self, es_results, faiss_results):
        # 合并两个搜索引擎的检索结果
        id_set = set()
        merged_news = []
        id_source = {}
        for res in es_results:
            id = int(res['id'])
            id_source[id] = [1, 0]
        for sim_res in faiss_results:
            res = sim_res['news']
            id = int(res['id'])
            if id in id_source:
                id_source[id][1] = 1
            else:
                id_source[id] = [0, 1]
        for res in es_results:
            id = int(res['id'])
            if id in id_set:
                continue
            id_set.add(id)
            if id in id_source:
                res['from_es'] = id_source[id][0]
                res['from_faiss'] = id_source[id][1]
            merged_news.append(res)
        for sim_res in faiss_results:
            res = sim_res['news']
            id = int(res['id'])
            if id in id_set:
                continue
            id_set.add(id)
            if id in id_source:
                res['from_es'] = id_source[id][0]
                res['from_faiss'] = id_source[id][1]
            merged_news.append(res)
        return merged_news


    def date_filter(self, news_date, merged_news):
        merged_news_filed = []
        for news in merged_news:
            if news.get('date', news.get('pub_date')) > news_date:
                continue
            merged_news_filed.append(news)
        return merged_news_filed


    def item_filter(self, target_news, merged_news):
        # target_news : {"id": nid, "title": title, "content": content, 'ents': ents, 'nums': nums, 'locs': locs}
        valid_news = []
        for news in merged_news:
            valid = True
            for ent in target_news['ents']:
                if ent not in news['content']:
                    valid = False
                    break
            if not valid:
                continue
            for loc in target_news['locs']:
                if loc not in news['content']:
                    valid = False
                    break
            if not valid:
                continue
            valid_news.append(news)
        return valid_news


    def sim_filter(self, target_news, candidate_news):
        target_head = text_util.get_head(target_news['title'], target_news['content'])
        content_list = [target_head]
        for news in candidate_news:
            head = text_util.get_head(news['title'], news['content'])
            content_list.append(head)
        embeddings = self.emb_model.encode(content_list)
        # print(embeddings.shape)
        target_vec = embeddings[:1]
        candidate_vecs = embeddings[1:]
        # print(target_vec.shape)
        # print(candidate_vecs.shape)
        sims = np.dot(target_vec, candidate_vecs.T)
        # print(sims.shape)
        valid_news = []
        valid_sims = []
        for i in range(0, sims.shape[1]):
            if sims[0][i] > 0.8 or sims[0][i] < 0.6:
                continue
            valid_news.append(candidate_news[i])
            valid_sims.append(sims[0][i])
            # print(sims[0][i], candidate_news[i])
        return valid_news, valid_sims


    def llm_filter(self, target_news, candidate_news, ents, locations):
        valid_news = []
        target_imp_para = text_util.get_important_paragraph(ents, locations, target_news['content'])
        target_txt = target_news['title'] + '\n' + target_imp_para
        target_txt = target_txt[:500]
        for news in candidate_news:
            old_imp_para = text_util.get_important_paragraph(ents, locations, news['content'])
            old_txt = news['title'] + '\n' + old_imp_para
            old_txt = old_txt[:500]
            logger.debug('----------------------------------------')
            if not self.same_thing(target_txt, old_txt):
                continue
            if not self.conflict(target_txt, old_txt):
                continue
            valid_news.append(news)
        return valid_news


    def same_thing(self, target_txt, old_txt):
        prompt = '请阅读以下两个文本，分别各用一句话总结两个文本的主要内容，并判断两个文本的主要内容是否涉及了同一件事情，以“是、否”做出回答。文本1：【%s】。文本2：【%s】。' % (
        target_txt, old_txt)
        logger.debug(f'same_thing: {prompt}')
        answer, used_token = self.llm.api(prompt)
        logger.debug(f'same_thing answer: {answer}')
        answer_lines = p_split_answer.split(answer.strip())
        if answer_lines[-1].endswith('否') or answer_lines[-1].endswith('没有') or answer_lines[-1].endswith('不是'):
            return False
        return True


    def conflict(self, target_txt, old_txt):
        prompt = '请阅读以下两个文本并判断两个文本的主要内容是否存在冲突，以“是、否”做出回答。文本1：【%s】。文本2：【%s】。' % (target_txt, old_txt)
        # print(prompt)
        logger.debug(f'confict: {prompt}')
        answer, used_token = self.llm.api(prompt)
        logger.debug(f'confict answer: {answer}')
        answer_lines = p_split_answer.split(answer)
        if '否' in answer_lines[0] or '没有' in answer_lines[0]:
            return False
        return True


def run():
    p_tit = re.compile('\W')
    task1_pos_file = '../dataset/CNCD.jsonl.task1.positive'

    conf = {}
    conf['data_path'] = '../model'
    conf['emb_model_path'] = '../model/BAAI/bge-base-zh-v1.5'
    checker = Worker(json.dumps(conf))

    step = 400
    # order:1-5
    order = 5
    out_file = 'CNCD.jsonl' + '.task2.pred_ent_sim_llm' + f'.{order}'
    ofile = open(out_file, 'w', encoding='utf8')
    with open(task1_pos_file) as fp:
        for lid, line in enumerate(fp):
            if lid < step * (order-1):
                continue
            if lid >= step * order:
                break
            line = line.strip()
            news = json.loads(line)
            id = news['id']
            title = news['title']
            content = news['content']
            news['pubDate'] = news['date']

            res_json = checker.process(json.dumps(news, ensure_ascii=False))
            res_data = json.loads(res_json)

            if res_data['stat']:
                logger.error(res_data['errMessage'])
                break
            if not res_data['message']:
                continue
            if not res_data['message'][0]:
                continue
            output = (news['id'], res['id'])
            #  output = {'label':1, 'news':news, 'result_news':res}
            #  ofile.write(f'{json.dumps(output, ensure_ascii=False)}\n')
            ofile.write(f'{str(output)}\n')
            logger.info('------------------------------------------------------------------------')
    ofile.close()


if __name__ == '__main__':
    USE_ENT_FILTER = False
    USE_SIM_FILTER = False
    run()
