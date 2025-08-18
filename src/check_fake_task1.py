# -*- coding: utf-8 -*-
# only for task1
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

logger = log_util.getLogger(__name__)

negtive_pattern = re.compile(r'辟谣|澄清|网传|疯传|谣言|虚假报道|造谣|严重失实|[为系](?:错误解读|媒体误读|不实信息)|不属实|[：:]不实|(?:否认|回应)[\u4e00-\u9fa5]*(?:网传|传闻)')
non_neg_pattern = re.compile(r'互联网传[统播媒]|网传[播媒]|河道澄清剂')
p_split_answer = re.compile('[。\n\r]+')

log_util.debug(__name__, True)

class Worker():
    def __init__(self, parameter):
        conf = json.loads(parameter)
        data_path = conf['data_path']
        self.llm = llm_worker.LlmWorker(data_path, use_buffer=True)
        self.version = conf.get('version', '1.0')


    def process(self, parameter):
        """
        input:{'title':title, 'content':content, 'date':'YYYY-mm-dd', 'id':id}
        """
        try:
            result = self.process0(parameter)
            return json.dumps({'message':[result], 'stat':0, 'version':self.version})
        except:
            logger.error(traceback.format_exc())
            return json.dumps({'message': [], 'stat': 1, 'errorMessage':traceback.format_exc(), 'version': self.version})


    def process0(self, parameter):
        input_data = json.loads(parameter)
        title = input_data['title']
        content = input_data['content']
        nid = input_data['id']
        news_date = input_data['date']
        # 首先判断输入新闻是否为否认事件
        # 先以模板判断
        if not self.pattern_match(title, content):
            return False
        # 再以LLM判断
        message = [
            {"role": "system",
             "content": "你是一个擅长阅读理解新闻的专家。阅读给出的新闻内容然后回答：\n根据给出的新闻回答新闻的主要内容是否针对某些已经披露的事情进行了明确地否认，以“是”或“否”进行回答；"},
            {"role": "user",
             "content": "特斯拉要在沙特建厂？马斯克在线辟谣\n9月18日，《华尔街日报》援引知情人士的消息报道称，沙特阿拉伯正与美国电动汽车制造商特斯拉就在沙特建立制造工厂进行初步谈判。 报道称，沙特阿拉伯一直在向特斯拉抛出橄榄枝，试图用从刚果民主共和国等国购买特斯拉电动汽车所需的一定数量的金属和矿产的权利来吸引其到当地建厂。 据悉，沙特正在考虑的一项举措是向大宗商品交易商Trafigura提供融资，帮助其完成刚果的一个钴铜项目，该项目可能有助于为特斯拉的一家工厂提供供应。此前，在成本不断上升和钴价持续低迷的情况下，Trafigura正在评估其对刚果Mutoshi项目的选择。 沙特一直在努力使其经济摆脱对石油的依赖，除了尝试吸引特斯拉之外，该国主权财富基金还是美国电动汽车初创公司Lucid Group 的主要投资者。 针对上述报道，特斯拉首席执行官埃隆·马斯克在社交媒体平台X上发帖进行了否认，而沙特阿拉伯的公共投资基金（Public Investment fund）拒绝置评。 特斯拉目前在全球拥有6家工厂，并正在墨西哥北部新莱昂州建设第七家工厂。今年5月，马斯克曾表示，特斯拉可能会在今年年底前敲定下一个工厂的最终选址。今年8月，特斯拉表示有兴趣在印度建立一家生产低成本电动汽车的工厂。日前，外媒又报道称土耳其总统雷杰普·塔伊普·埃尔多安（Recep Tayyip Erdogan）在美国纽约与马斯克会面，并邀请特斯拉在土耳其设立工厂。9月18日，马斯克还在加州会见了以色列总理Benjamin Netanyahu。 特斯拉的目标是到2030年每年销售2000万辆汽车，较2022年的130万辆将翻数倍。"},
            {"role": "assistant",
             "content": "是"},
            {"role": "user",
             "content": title + '\n' + content}
        ]

        logger.info(f'title:{title}')
        answer, usage = self.llm.api('', message=message)
        logger.info(f'answer:{answer}')
        p_negtive = re.compile('否')
        if p_negtive.search(answer):
            return False
        return True


    def pattern_match(self, title, content):
        sents = text_util.get_sentence(content)
        head_part = ''
        head_sen = ''
        if len(sents) > 1 and sents[0]:
            head_sen = sents[0] + sents[1]
            head_part = title + "。" + head_sen
        else:
            head_part = title
        sub_head_part = non_neg_pattern.sub('@|@', head_part)
        if not negtive_pattern.search(sub_head_part):
            return False
        return True


def run():
    p_tit = re.compile('\W')
    news_file = '../dataset/CNCD.jsonl'
    sta_date = '2023-03-01'
    end_date = '2023-05-31'
    out_file = news_file + '.task1.' + sta_date + '-' + end_date
    ofile = open(out_file, 'w', encoding='utf8')
    tit_set = set()

    conf = {}
    conf['data_path'] = '../model'
    conf['emb_model_path'] = '../model/BAAI/bge-base-zh-v1.5'
    checker = Worker(json.dumps(conf))
    skip = True
    with open(news_file, encoding='utf8') as fp:
        for lid, line in enumerate(fp):
            if lid % 1000 == 0:
                logger.info(f'line {lid} done')
            line = line.strip()
            news = json.loads(line)
            id = news['id']
            title = news['title']
            content = news['content']
            news['pubDate'] = news['date']
            if news['date'] < sta_date:
                continue
            if news['date'] > end_date:
                break

            res_json = checker.process(json.dumps(news, ensure_ascii=False))
            res_data = json.loads(res_json)

            if res_data['stat']:
                logger.error(res_data['errMessage'])
                break
            if not res_data['message']:
                continue
            if not res_data['message'][0]:
                continue
            output = {'news':news, 'result':res_data['message']}
            ofile.write(f'1\t{json.dumps(output, ensure_ascii=False)}\n')
    ofile.close()


if __name__ == '__main__':
    run()
