import json
from lxml import etree, html


class parser_tictoc:
    def datas(self, text, type) -> None:
            doc = html.fromstring(text)

            _desc = doc.xpath('//meta[@name="description"]/@content')[0]
            _data = json.loads(doc.xpath('//script[@id="SIGI_STATE"]/text()')[0])

            if   "hashtag_info" == type:
                return _desc
            elif "hashtag_list" == type:
                _item = _data["ItemModule"]
                return {
                    "itemlist": ["https://www.tiktok.com/@" + _item[m]['author'] + "/video/" + _item[m]['id'] for m in _item],
                    "itemstat": [[_item[m]['author'], _item[m]['createTime'], _item[m]['desc'], _item[m]['music'], _item[m]['stats']] for m in _item]
                }
            elif "music_list" == type:
                _item = _data["ItemModule"]
                return {
                    "itemlist": ["https://www.tiktok.com/@" + _item[m]['author'] + "/video/" + _item[m]['id'] for m in _item],
                    "itemstat": [[_item[m]['author'], _item[m]['createTime'], _item[m]['desc'], _item[m]['music'], _item[m]['stats']] for m in _item]
                }
            elif "user_info" == type:
                _user = _data["UserModule"]
                return _user
