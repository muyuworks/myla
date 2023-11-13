import asyncio
import myla.llms as llms

DOCS = """
[{"doc": {"page_content": "店铺\u0001你好，请问欧舒丹有什么适合送男士的礼物推荐吗？", "metadata": {"source": "chat", "seq_num": 438, "category": "店铺", "query": "你好，请问欧舒丹有什么适合送男士的礼物推荐吗？", "response": ["商品推荐:552606197525\u0001清新马鞭草沐浴啫喱", "亲马鞭草的适合的哦", "马鞭草系列是欧舒丹比较受欢迎的一款香型，天然的柠檬草本香气，让您肌肤充满活力，舒缓压力，是一年四季的必备款！"], "msg_id": "yanmin01234-yanmin01234-2023-05-03 15:55:58", "item_id": [], "meta": {"use_origin_question": false, "use_origin_answer": true}, "qa_type": "query"}}, "score": 0.9233652353286743}, {"doc": {"page_content": "商品\u0001甜扁桃紧致沐浴油\u0001那可以帮忙定制贺卡吗？还有礼袋，我想买这个甜扁桃紧致沐浴油作为礼物送给朋友，但是希望可以更有心意，可以加上一些定制的元素，比如定制的贺卡和礼袋，这样会更有意义。", "metadata": {"source": "chat", "seq_num": 5377, "category": "商品\u0001甜扁桃紧致沐浴油", "query": "那可以帮忙定制贺卡吗？还有礼袋，我想买这个甜扁桃紧致沐浴油作为礼物送给朋友，但是希望可以更有心意，可以加上一些定制的元素，比如定制的贺卡和礼袋，这样会更有意义。", "response": ["亲 店铺是不支持的哦", "抱歉未能帮您传达心意，目前店铺暂时是不支持写纸条、卡片，您可以拍下产品之后单独写一张贺卡发出，告知好友有一个在途礼物，相信好友收到贺卡和礼物会有一个期待和双重惊喜的哦", "亲，很抱歉未能帮助到您，目前活动无礼品袋，但一个包裹会默认配送一个礼盒哦~", "亲目前是没有礼袋的   考虑到您是送人 这边可以帮您特殊申请礼袋哦", "您先拍1分钱等系统发货确认收货后，您拍正装单笔实付满200会一起发出"], "msg_id": "chenshasha1234-chenshasha1234-2023-05-02 14:14:31", "item_id": ["42125022611"], "meta": {"use_origin_question": false, "use_origin_answer": true}, "qa_type": "query"}}, "score": 1.0160454511642456}, {"doc": {"page_content": "商品\u0001甜蜜樱花香氛沐浴啫喱\u0002洗发水合集草本平衡头皮护理清洁丰盈蓬松控油男女士洗头水\u0001请问300毫升的洗发水礼盒赠品中是否包含干发帽？如果买五套礼盒，赠品会有多送吗？", "metadata": {"source": "chat", "seq_num": 2791, "category": "商品\u0001甜蜜樱花香氛沐浴啫喱\u0002洗发水合集草本平衡头皮护理清洁丰盈蓬松控油男女士洗头水", "query": "请问300毫升的洗发水礼盒赠品中是否包含干发帽？如果买五套礼盒，赠品会有多送吗？", "response": ["感谢您对欧舒丹产品的支持和喜爱，但是套装产品和礼赠是系统自动识别固定的，不支持更换和调整哦，谢谢您的理解~"], "msg_id": "關于莉莉zhou-關于莉莉zhou-2023-03-02 20:37:56", "item_id": ["42589568633", "535618134511"], "meta": {"use_origin_question": false, "use_origin_answer": true}, "qa_type": "query"}}, "score": 1.0173909664154053}, {"doc": {"page_content": "商品\u0001洗发水草本强韧平衡洗发露头皮清洁蓬松\u0001请问除了草本护发和草本木梳，还有其他的礼赠吗？", "metadata": {"source": "chat", "seq_num": 3875, "category": "商品\u0001洗发水草本强韧平衡洗发露头皮清洁蓬松", "query": "请问除了草本护发和草本木梳，还有其他的礼赠吗？", "response": ["会员预定臻享『正装礼』： \n   随机草本护发 500ml\n   草本木梳", "亲，您可以看一下，这是活动礼赠哦"], "msg_id": "蒙奇奇5835-蒙奇奇5835-2023-03-05 20:55:16", "item_id": ["657938228793"], "meta": {"use_origin_question": false, "use_origin_answer": true}, "qa_type": "query"}}, "score": 1.0250369310379028}]
"""

QUERY = "送给谢顶男票的礼物"

INSTRUCTIONS = """
你是专业的问答分析助手。下面是JSON格式的问答记录。
<问答记录开始>
{docs}
<问答记录介绍>

请根据问答记录生成新问题的候选回答。
新问题: {query}
候选回答:
"""

async def main():
    r = await llms.get().chat(messages=[{
        "role": "system",
        "content": INSTRUCTIONS.format(docs=DOCS, query=QUERY)
    }], stream=False)
    print(r)


if __name__ == '__main__':
    import dotenv
    dotenv.load_dotenv(".env")

    asyncio.run(main=main())