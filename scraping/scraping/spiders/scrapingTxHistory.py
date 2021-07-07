import scrapy
import json

class MyItem(scrapy.Item):
    txHash = scrapy.Field()
    date = scrapy.Field()
    BALN_claimed = scrapy.Field()
    bnUSD_claimed = scrapy.Field()
    sICX_claimed = scrapy.Field()


class TxSpider(scrapy.Spider):
    name = "iconTx"
    start_urls = ['https://tracker.icon.foundation/addresstx/hxcb3204684516b1bb89d0e4c09a1cea848db2a7f1/1?count=100']
    headers = {
        "authority": "tracker.icon.foundation",
        "method": "GET",
        "path": "/v3/address/txList?page=1&count=100&address=hxcb3204684516b1bb89d0e4c09a1cea848db2a7f1",
        "scheme": "https",
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en, ur; q=0.9, ko;q=0.8",
        "referer": "https://tracker.icon.foundation/addresstx/hxcb3204684516b1bb89d0e4c09a1cea848db2a7f1/1?count=100",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36"
    }

    def __init__(self, address='', **kwargs):  # The category variable will have the input URL.
        super().__init__(**kwargs)
        self.userAddress = address

    custom_settings = {'FEED_URI': 'outputfile.json',
                       'CLOSESPIDER_TIMEOUT': 15}  # This will tell scrapy to store the scraped data to outputfile.json and for how long the spider should run.

    def parse(self, response):
        url = f'https://tracker.icon.foundation/v3/address/txList?page=1&count=100&address={self.userAddress}'
        yield scrapy.Request(url,
                             callback=self.parse_json,
                             headers=self.headers)

    def parse_json(self, response):
        raw_data = response.body
        data = json.loads(raw_data)

        for tx in data["data"]:
            if tx['toAddr'] == "cx203d9cd2a669be67177e997b8948ce2c35caffae":
                tx_hash = tx['txHash']
                yield scrapy.Request(
                    f"https://tracker.icon.foundation/v3/transaction/txDetail?txHash={tx_hash}",
                    callback=self.parse_Tx,
                    headers=self.headers,
                )

    def parse_Tx(self, response):
        data = json.loads(response.body)
        yield MyItem(
            txHash=data["data"]["txHash"],
            date = data["data"]["createDate"],
            BALN_claimed=data["data"]["tokenTxList"][0]["quantity"],
            bnUSD_claimed=data["data"]["tokenTxList"][1]["quantity"],
            sICX_claimed=data["data"]["tokenTxList"][2]["quantity"],
        )
