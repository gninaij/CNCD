# -*- coding: utf-8 -*-
from openai import OpenAI
import json
import re
import os
try:
    import pysnooper
except:
    pass

import log_util

logger = log_util.getLogger(__name__)

class LlmWorker:
    def __init__(self, data_path, buffer_file=None, new_buffer_file=None, use_buffer=False):
        global MODEL
        #  deepseek官方
        self.api_key = 'your api key'
        self.client = OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")
        self.model="deepseek-chat"
        self.use_buffer = use_buffer
        if self.use_buffer:
            if buffer_file:
                self.buffer_file = buffer_file
            else:
                self.buffer_file = os.path.join(data_path, 'llm.buffer')
            if not new_buffer_file:
                self.new_buffer_file = self.buffer_file
            else:
                self.new_buffer_file = new_buffer_file
            self.buffer = {}
            if os.path.exists(self.buffer_file):
                with open(self.buffer_file, encoding='utf8') as fp:
                    for line in fp:
                        line = line.strip()
                        data = json.loads(line)
                        self.buffer[data['prompt']] = data
            self.out_buffer = open(self.new_buffer_file, 'a', encoding='utf8')
        self.p_json = re.compile('```json(.+?)```')
        self.p_json2 = re.compile('json({.+}|\[.+\])')
        self.p_json3 = re.compile('({.+}|\[.+\])')
        self.p_endl = re.compile('[\r\n]')
        self.p_null = re.compile('"?null"?')
        self.completion_tokens = 0
        self.prompt_tokens = 0
        logger.info('LLM_worker initialized')


    def __del__(self):
        if self.use_buffer:
            self.out_buffer.close()
            del self.buffer
            del self.client


    def calc_tokens(self, token_usage):
        self.completion_tokens += token_usage.completion_tokens
        self.prompt_tokens += token_usage.prompt_tokens


    def print_tokens(self):
        print('completion tokens:%d' % self.completion_tokens)
        print('prompt tokens:%d' % self.prompt_tokens)


    def api(self, content, message=None):
        #  print(json.dumps({'prompt':content}, ensure_ascii=False))
        if self.use_buffer and content and content in self.buffer:
            answer = self.buffer[content]['answer']
            # print('buffer')
            logger.debug('answer:%s' % answer)
            return answer, {'completion_tokens':0, 'prompt_tokens':0}
        if self.use_buffer and not content and message:
            key = str(message)
            if key in self.buffer:
                answer = self.buffer[key]['answer']
                # print('buffer')
                logger.debug('answer:%s' % answer)
                return answer, {'completion_tokens': 0, 'prompt_tokens': 0}
        logger.debug('prompt:%s' % content)
        if content and not message:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": content},
                ],
                stream=False,
                top_p=0.5
            )
        elif message:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=message,
                stream=False,
                top_p=0.5
            )
        else:
            return '', {}
        answer = response.choices[0].message.content

        if self.use_buffer:
            if content:
                save_data = {'prompt': content, 'answer': answer}
                self.out_buffer.write('%s\n' % json.dumps(save_data, ensure_ascii=False))
                self.buffer[content] = save_data
            elif key:
                save_data = {'prompt': key, 'answer': answer}
                self.out_buffer.write('%s\n' % json.dumps(save_data, ensure_ascii=False))
                self.buffer[key] = save_data

        logger.debug('answer:%s' % answer)
        # print(answer)
        # print(response.usage)
        self.calc_tokens(response.usage)
        return answer, response.usage


    # @pysnooper.snoop('./debug.log')
    def get_json(self, answer, use_llm=True):
        # 从answer中提取json结构
        # answer:要提取json的文本
        # use_llm:是否使用大模型修复json格式数据

        answer = self.p_endl.sub('', answer)
        answer = self.p_null.sub('""', answer)
        #  print(answer)
        patterns = [self.p_json, self.p_json2, self.p_json3]
        matched_txt = ''
        for pattern in patterns:
            m = pattern.search(answer)
            if m:
                matched_txt = m.group(1)
                break
        if not matched_txt:
            #  取第一个大括号内的内容
            stack = []
            for i, c in enumerate(answer):
                if c == '{':
                    stack.append(i)
                elif c == '}':
                    if stack:
                        s = stack.pop()
                    else:
                        break
                    if not stack:
                        matched_txt = answer[s:i+1]
                        break
        if matched_txt:
            #  print(matched_txt)
            #  json_data = eval(matched_txt)
            try:
                json_data = json.loads(matched_txt)
                if json_data:
                    json_data = self.set2list(json_data)
            except:
                if use_llm:
                    prompt = '从下面的内容中提取出json格式的部分，并调整为正确的json格式：%s' % m.group(1)
                    #  print(prompt)
                    json_answer, json_usage = self.api(prompt)
                    #  print(json_answer)
                    #  print('---------------------------')
                    json_data = self.get_json(json_answer, use_llm=False)
                    if json_data:
                        json_data = self.set2list(json_data)
                    return json_data
                else:
                    return None
        else:
            return None
        return json_data


    #  @pysnooper.snoop('./debug.log')
    def set2list(self, json_data):
        if isinstance(json_data, list):
            for i, v in enumerate(json_data):
                if isinstance(v, set):
                    json_data[i] = list(v)
                elif isinstance(v, list):
                    json_data[i] = self.set2list(v)
                elif isinstance(v, dict):
                    json_data[i] = self.set2list(v)
                else:
                    pass
        elif isinstance(json_data, dict):
            for k, v in json_data.items():
                if isinstance(v, set):
                    json_data[k] = list(v)
                elif isinstance(v, list):
                    json_data[k] = self.set2list(v)
                elif isinstance(v, dict):
                    json_data[k] = self.set2list(v)
                else:
                    pass
        elif isinstance(json_data, set):
            json_data = list(json_data)
            for i, v in enumerate(json_data):
                if isinstance(v, set):
                    json_data[i] = list(v)
                elif isinstance(v, list):
                    json_data[i] = self.set2list(v)
                elif isinstance(v, dict):
                    json_data[i] = self.set2list(v)
                else:
                    pass
        else:
            pass
        return json_data


def test():
    worker = LlmWorker('../data/buffer_data')
    prompt = '你好'
    # print(prompt)
    answer, usage_tokens = worker.api(prompt)
    print(answer)
    #  print(usage_tokens)
    #  print(worker.get_json(answer))
    # print(worker.get_json(answer))


if __name__ == '__main__':
    test()
