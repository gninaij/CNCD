# -*- coding: utf-8 -*-
import re
import os
import json
try:
    import pysnooper
except:
    pass

p_para = re.compile('[\r\n]+')

def get_head(title, content):
    # 取title和首段（>=20字）作为head
    paras = p_para.split(content)
    if paras:
        if len(paras[0]) >= 20:
            if len(paras[0]) >= 200:
                head = title + '\n' + paras[0][:200]
            else:
                head = title + '\n' + paras[0]
        elif len(paras) > 1:
            if len(paras[1]) >= 200:
                head = title + '\n' + paras[1][:200]
            else:
                head = title + '\n' + paras[1]
        else:
            head = title + '\n' + paras[0]
    else:
        head = title
    return head


p_sent = re.compile('([。！？…\?\!])')
def get_sentence(content):
    sents = p_sent.split(content)
    return sents


def sort_corpus_bydate():
    # 把新闻按日期升序排列
    corpus_file = 'all_news20231001-20240107.fil'
    dates = set()
    date_dir = './date_news'
    ofiles = {}
    with open(corpus_file, encoding='utf8') as fp:
        for lid, line in enumerate(fp):
            if lid % 100000 == 0:
                print(lid)
            line = line.strip()
            tlist = line.split('\t')
            date = tlist[1][:10]
            if date not in dates:
                out_file = os.path.join(date_dir, date)
                ofiles[date] = open(out_file, 'w', encoding='utf8')
                dates.add(date)
            ofiles[date].write(f'{line}\n')

    dates = list(dates)
    dates.sort()
    full_out_file = corpus_file + '.sort'
    ofile_full = open(full_out_file, 'w', encoding='utf8')
    for date in dates:
        ofiles[date].close()
        out_file = os.path.join(date_dir, date)
        with open(out_file, encoding='utf8') as fp:
            for line in fp:
                ofile_full.write(line)
        print(f'{out_file} done')


#  @pysnooper.snoop('./debug.log')
def get_important_paragraph(ents, locations, content):
    # get paragraph which have ents/locations from news'content
    paras = p_para.split(content)
    sub_set = {'(', ')', '[', ']', '+', '-', '.', '*'}
    rule = ''
    if ents:
        rule = '|'.join(ents)
    if locations and not rule:
        rule = '|'.join(locations)
    if not rule:
        return ''
    rule_list = []
    for c in list(rule):
        if c in sub_set:
            rule_list.append('\\')
        rule_list.append(c)
    rule = ''.join(rule_list)
    rule = f'({rule})'
    #  print(rule)
    p = re.compile(rule)
    # 统计每个段落出现关键词的数量（不计重复），取数量最大的段落覆盖的范围
    cnt_list = []  # [(para_id, kw_cnt)]
    for i, para in enumerate(paras):
        parts = p.split(para)
        if len(parts) == 1:
            cnt_list.append((i, 0))
            continue
        kw_list = [kw for kw in parts[1::2]]
        kw_cnt = len(set(kw_list))
        cnt_list.append((i, kw_cnt))
    cnt_list.sort(key=lambda d:d[1], reverse=True)
    sta = 999999
    end = -1
    for para_id, kw_cnt in cnt_list:
        if kw_cnt < cnt_list[0][1] and kw_cnt <= 1:
            break
        if para_id < sta:
            sta = para_id
        if para_id > end:
            end = para_id
    if end < 0:
        return ''

    if sta >= 0 and end >= sta:
        imp_para = '\n'.join(paras[sta:end+1])
    else:
        return ''
    return imp_para



if __name__ == '__main__':
    #  sort_corpus_bydate()
    ents = ["美团", "(硅谷)银行+其他-银行[美国]"]
    #  ents = ["美团", "王兴"]
    locations = []
    content = '过去的20年，互联网+VC相辅相成的爆发成就了硅谷，也造就了SVB这家特殊的“银行”。如今，整个互联网的宏大叙事已经远去，所谓的互联网+硅谷的造富神话也开始成为历史。\n硅谷银行（Silicon Valley Bank，简称SVB）一夜破产，科技投资人和创业者阴云笼罩。\n“没想到一觉醒来，居然赶上了银行倒闭，人生完整了。”中国医疗初创公司创业者安迪（化名）3月11日午间发了一条微信朋友圈。他的公司大部分美元资产都存在硅谷银行，主要用于美国办公室人员的工资发放。\n另一位业内人士在谈及此次硅谷银行事件造成的负面影响时对记者透露，有初创企业因此损失上亿人民币。\n美国著名创业孵化器Y Combinator CEO更是将硅谷银行的后果称为“初创企业的灭绝级别事件”，他称YC 1/3的项目约1000多个创业公司所有的钱都在硅谷银行，下周甚至发不了工资和房租，而保险公司理赔的上限是25万美元。\n互联网投资人庄明浩表示，如果说过去的20年，互联网+VC相辅相成的爆发成就了硅谷，这种效用同时造就了SVB这家特殊的“银行”。如今，整个互联网的宏大叙事已经远去，所谓的互联网+硅谷的造富神话也开始成为历史。\n一大波风投与创业公司受影响\n“没想到连SVB都要遭遇金融信用危机，这可是大多数投资机构和创业公司的首选开户行。”一位科技领域创业者这样感慨。\n1983年成立于美国的硅谷银行一度被认为是初创公司的“金主”和“命脉”， 在硅谷高科技产业高速发展之际，它凭借低息募资、面向大银行尚未重视的中小企业，迅速开辟出灵活的发展路径，成功帮助过Facebook、twitter等明星企业。\nappWorks合伙人、具备多年募资经验的詹益鉴总结，硅谷银行之所以能够拥有近一半的初创公司市占率，关键在于其核心产品风险债，可以帮助创业者减少股权稀释，帮助投资人降低现金流风险，只要公司成长与获利能力高于资金成本，实际便能获得投资人、创业公司与风险债发行者三方共赢的局面。\n为了让旗下被投公司获得风险债额度，詹益鉴称，许多创投机构会要求被投公司尽早到SVB开设账户、积累往来记录与财务资料，并将投资资金存放到该账户中，降低汇兑费用与手续时间。其后，随着老牌或大型初创机构对SVB的信任与依赖，想在硅谷获得投资或已被投的创业公司，几乎都有SVB账户。\n“我们使用硅谷银行也是因为它的服务好，而且非常便捷。”安迪告诉第一财经记者。\n但这样的特性使得硅谷银行对于行业的繁荣与萧条周期特别敏感。今日，一段美团曾晒出硅谷银行存款6000多万美元的旧闻被重新提起。有消息称美团创始人王兴今日已回应“我们很多年前就转用大银行了。”第一财经记者就此询问，截至发稿美团公司方面未予以回应。\n但安迪所在的企业没有这么幸运。他告诉第一财经记者：“从昨天开始我们就一直在设法转钱出去，但是还没有转出来，银行就先倒闭了，一切都发生得太快了。”目前，银行网站的状态显示正在维护中。\n不过，因为企业规模不大，安迪的公司存在硅谷银行的美元资金并不多，涉及数十万美元的资金。他还向第一财经记者透露：“至少在我的朋友圈就有好多家中国初创公司也把钱存在硅谷银行。”\n安迪称，相比一些存款好几亿美元的大型科技公司来讲，自己就是损失了也还不算多，保险公司理赔上限25万美元，风险相对可控。\n以流媒体技术公司Roku为例，该公司在提交给美国证券交易委员会的一份文件中披露，该公司在硅谷银行持有近5亿美元现金，占现金流比例超过四分之一。Roku还称，其在硅谷银行的大部分存款都没有投保，不知道公司能够在多大程度上收回现金存款。\n“元宇宙第一股”游戏公司Roblox在一份文件中表示，其30亿美元现金中的5%存在硅谷银行。\n除了互联网企业，加密资产客户也被硅谷银行纳入可接纳范畴，虽然所设敞口并不大。据统计，Blockchain Capital、Castle Island Ventures、Dragonfly 与Pantera 都与硅谷银行有关系。\n另据加密货币领域稳定币发行商Circle公司表示，截至1月17日，总部位于美国的稳定币发行人Circle在硅谷银行持有其USDC（市场第二大稳定币）稳定币的部分现金储备。\n负面影响还在持续蔓延。第一财经记者了解到，多家LP（Limited Partners，有限合伙人）机构开始询问自己投的基金有没有将钱放在SVB里。有LP发朋友圈称，自己所投的基金连夜发邮件告知没有将钱存在硅谷银行，而那些没有发邮件的，大概率是遇到了麻烦。\n恐慌情绪背后\n传奇基金经理、潘兴广场创始人比尔·阿克曼（Bill Ackman）在推文中表示，由于风险资本支持的公司依赖SVB获取贷款和运营资金，因此这家硅谷第一大银行倒闭可能会摧毁经济的关键长期推动力，SVB一旦倒闭，将有更多的银行面临挤兑和倒闭，届时多米诺骨牌会接连倒下。\n“大家已经开始把账户转到更大规模的银行，担心小银行爆雷。”一位硅谷的从业者对第一财经记者说。\n还有一位正在计划将资金从BOA银行转到Chase银行的硅谷人士对第一财经表示，“Chase的银行工作人员忙疯了，说不少客户连夜开户，预计下周一还将有大量客户紧急把资金转入Chase里。”\n回溯这场危机，互联网投资人庄明浩认为，2022年下半年开始的长加息周期令债券价格不断下跌，硅谷银行出现高额浮亏。近日，SVB启动资本动作，出售大部分可供出售金融资产（AFS）以换取流动性来支付存款提款。此次出售涉及价值210亿美元的债券，造成18亿美元实际亏损。同时，SVB还将通过出售普通股和优先股等股权融资方式，募集22.5亿美元的资金。CEO贝克尔又向最大客户群风险投资者们争取支持，没想到这些机构转身就劝说被投企业们提前取出资金，进而引发挤兑风险。\n庄明浩对第一财经记者表示，很多天使轮与A轮阶段的早期公司没有资产配置的概念，也一般不太会开很多银行的账户，自身业务可能还没赚钱甚至收入都没有，主要依靠VC投资款活着，这种情况不分中美，都会受到硅谷银行事件的巨大冲击。\n“从心理上讲，这是一个打击，因为每个人都意识到事情是多么不堪一击。”为初创公司提供税务、会计和人力资源服务的咨询机构Kruze Consulting运营主管Scott Orn表示。\nOrn将硅谷银行称为“硅谷皇冠上的明珠”。对于他的数百个客户来说，硅谷银行的撤资可能会使初创公司借钱成本变得更加昂贵。他希望硅谷银行能够度过这个困难时期，甚至有可能被一家更大的银行收购。\n目前来看，美国政府已经介入，但对SVB最大客户群——风险投资机构与初创公司的负面影响已经造成，尤其是在资金流动性压力方面。\n硅谷技术VC Fusion Fund创始人张璐在接受第一财经采访时说，这一事件对于科技创投领域的资金活跃度影响巨大，尤其对初创企业影响不小，但硅谷技术创新的趋势不会因为资金的问题就出现倒退。\n还有用户提议推特应该收购硅谷银行并将它变成一家数字银行，马斯克对此评论称持开放态度。\n硅谷银行的倒闭正值科技行业面临挑战之际。 不断上升的利率侵蚀了便宜的资金渠道。根据CBInsights今年1月份发布的数据，2022年美国的风险投资较上年下降了37%。\n与此同时，宏观经济不确定性和衰退担忧促使一些广告商和消费者收紧支出，削弱了科技行业的收入驱动力，大型科技企业陷入了大规模裁员，重新关注以“效率”为标志的成本削减计划。\n尽管一些经济学家认为，此次以科技行业为代表的硅谷银行的倒闭可能会破坏经济增长的驱动力，但一些金融人士认为，硅谷银行破产具有特殊性，广泛蔓延到金融行业的可能性不大。\n“硅谷银行破产主要是市场利率上升后，债券价格下降，而硅谷银行又不得以不低价大量出售手中的债券以应付投资者兑现需求。正如美国前财长萨默斯所说的，只要政府介入，不必太担心对金融系统其他部分的影响。”一位全球知名投行人士告诉第一财经记者。\n上述人士还表示，目前来看，一些美国大银行的情况远没有硅谷银行那么糟糕，因为它们的业务更多元化，而不是专注某些特定的高风险行业。\n海量资讯、精准解读，尽在新浪财经APP\n责任编辑：李铁民'
    print(get_important_paragraph(ents, locations, content))
