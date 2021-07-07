from app import app
import crochet
crochet.setup()  # initialize crochet before further imports
from flask import render_template, flash, jsonify, redirect
from app.forms import UserAddressForm
from app import network
from app import user_account
from scrapy import signals
from scrapy.crawler import CrawlerRunner
from scrapy.signalmanager import dispatcher
from scraping.scraping.spiders import scrapingTxHistory
import os
import pytz
from datetime import datetime

output_data = []
crawl_runner = CrawlerRunner()

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def index_page():
    form = UserAddressForm()
    day = network.getDay()
    network_info = network.networkData()
    new_user_account = user_account.user_account()

    if form.validate_on_submit():
        if new_user_account.updateUser(form.ICX_wallet_address.data, network_info[0], day):
            scrape(form.ICX_wallet_address.data)
            calculate_age()
            return render_template('index.html', form=form, user=new_user_account, networkInfo=network_info, history=output_data)

    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'{err_msg}', category='info')
    return render_template('index.html', form=form, user=new_user_account, networkInfo=network_info)

# crawl_runner = CrawlerRunner(get_project_settings()) if you want to apply settings.py


def scrape(wallet_address):
    output_data.clear()
    # run crawler in twisted reactor synchronously
    scrape_with_crochet(address=wallet_address)
    if os.path.exists("outputfile.json"):
        os.remove("outputfile.json")
    return jsonify(output_data)


@crochet.wait_for(timeout=60.0)
def scrape_with_crochet(address):
    # signal fires when single item is processed
    # and calls _crawler_result to append that item
    dispatcher.connect(_crawler_result, signal=signals.item_scraped)
    eventual = crawl_runner.crawl(
        scrapingTxHistory.TxSpider, address = address)
    return eventual  # returns a twisted.internet.defer.Deferred


def _crawler_result(item):
    output_data.append(dict(item))


def calculate_age():
    for i in range(len(output_data)):
        date_string = output_data[i]["date"]
        date_object = datetime.strptime(date_string[:19], "%Y-%m-%dT%H:%M:%S")
        age_delta = datetime.utcnow().replace(tzinfo=pytz.utc) - date_object.replace(tzinfo=pytz.utc)
        age = str(age_delta.days) + " days " + str(int(age_delta.seconds / 3600)) + " hours ago"
        output_data[i]["date"] = age

