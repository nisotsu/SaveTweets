import sys
from time import sleep
import json
import os
import traceback
import argparse
import datetime
from tqdm import tqdm
import requests
import snscrape.modules.twitter as sntwitter


def archive_tweet(access_key, secret, target_id, min_like, min_reply, min_retweet, min_quote, debug_flag, since_date, until_date):
    url_and_jobid_list = []
    
    since_date = datetime.datetime.strptime(since_date, "%Y-%m-%d").date()
    until_date = datetime.datetime.strptime(until_date, "%Y-%m-%d").date()
    print("Start archiving")
    print(f"[0]:https://twitter.com/{target_id}")
    MAX_ERROR_COUNT = 10
    for _ in range(MAX_ERROR_COUNT):
        try:
            headers = {
                "Accept":"application/json",
                "Authorization":f"LOW {access_key}:{secret}"
            }
            # sessionに空きが出るまでループ
            while True:
                res = requests.get("https://web.archive.org/save/status/user", headers=headers).json()
                res = res["available"]
                if res == 0:
                    print("Internet archive user-session-limit. wait 5 seconds")
                    sleep(5)
                else:
                    break
            payload = {"url":f"https://twitter.com/{target_id}"}
            res_dict = requests.post("https://web.archive.org/save",data=payload, headers=headers).json()
            if res_dict.get("status") == "error":
                raise ValueError("Internet archive error")
            else:
                url_and_jobid_list.append(res_dict)
            break
        except Exception as e:
            if debug_flag:
                print(traceback.format_exc())
            print("Wait 10 seconds due to error")
            sleep(10)

    tweets = sntwitter.TwitterUserScraper(target_id).get_items()
    for i,tweet in enumerate(tweets):
        if tweet.likeCount < min_like:
            print(f"[{i+1}]: Skipped. likecount < {min_like}")
            continue
        if tweet.replyCount < min_reply:
            print(f"[{i+1}]: Skipped. replycount < {min_reply}")
            continue
        if tweet.retweetCount < min_retweet:
            print(f"[{i+1}]: Skipped. retweetcount < {min_retweet}")
            continue
        if tweet.quoteCount < min_quote:
            print(f"[{i+1}]: Skipped. quotecount < {min_quote}")
            continue
        if tweet.date.date() > until_date:
            print(f"[{i+1}]: Skipped. tweetdate > {until_date}")
            continue
        if tweet.date.date() < since_date:
            print(f"[{i+1}]: Skipped. tweetdate < {since_date}")
            break

        print(f"[{i+1}]:{tweet.url}")
        MAX_ERROR_COUNT = 10
        for _ in range(MAX_ERROR_COUNT):
            try:
                headers = {
                    "Accept":"application/json",
                    "Authorization":f"LOW {access_key}:{secret}"
                }
                # sessionに空きが出るまでループ
                while True:
                    res = requests.get("https://web.archive.org/save/status/user", headers=headers).json()
                    res = res["available"]
                    if res == 0:
                        print("Internet archive user-session-limit. wait 5 seconds")
                        sleep(5)
                    else:
                        break
                payload = {"url":tweet.url}
                res_dict = requests.post("https://web.archive.org/save",data=payload, headers=headers).json()
                if res_dict.get("status") == "error":
                    raise ValueError("Internet archive error")
                else:
                    url_and_jobid_list.append(res_dict)
                break
            except Exception as e:
                if debug_flag:
                    print(traceback.format_exc())
                print("Wait 10 seconds due to error")
                sleep(10)

        sleep(5)
    return url_and_jobid_list

def check_archive(access_key, secret, url_and_jobid_list, debug_flag):
    first_num = 0
    success_num = 0
    failure_num = 0
    failure_urls = []
    print("Start checking archives")
    with tqdm(total=len(url_and_jobid_list)) as pgbar:
        for url_and_jobid in url_and_jobid_list:
            MAX_ERROR_COUNT = 10
            for _ in range(MAX_ERROR_COUNT):
                try:
                    headers = {
                        "Accept":"application/json",
                        "Authorization":f"LOW {access_key}:{secret}"
                    }
                    res_dict = requests.get(f"https://web.archive.org/save/status/{url_and_jobid['job_id']}", headers=headers).json()
                    if res_dict.get("status") == "success":
                        success_num += 1
                        if res_dict.get("first_archive") == True:
                            first_num += 1
                    elif res_dict.get("status") == "error":
                        failure_num += 1
                        if res_dict.get("exception") is not None:
                            print(res_dict.get("exception"))
                        if res_dict.get("status_ext") is not None:
                            print(res_dict.get("status_ext"))
                        if res_dict.get("message") is not None:
                            print(res_dict.get("message"))
                        failure_urls.append(url_and_jobid["url"])
                    elif res_dict.get("status") == "pending":
                        url_and_jobid_list.append(url_and_jobid)
                        pgbar.total = len(url_and_jobid_list)
                        sleep(5)
                    break
                except KeyboardInterrupt as e:
                    print(f"success:{success_num} first-archive:{first_num} failure:{failure_num}")
                    if failure_num > 0:
                        print("failure urls")
                        for url in failure_urls:
                            print(url)
                    raise KeyboardInterrupt
                except Exception as e:
                    if debug_flag:
                        print(traceback.format_exc())
                    print("Wait 10 seconds due to error")
                    sleep(10)
            pgbar.update(1)
            sleep(1)

    print(f"success:{success_num} first-archive:{first_num} failure:{failure_num}")
    if failure_num > 0:
        print("failure urls")
        for url in failure_urls:
            print(url)

def main():
    KEYS_PATH = "./key.json"
    access_key = ""
    secret = ""
    
    parser = argparse.ArgumentParser(description="A simple program to archive tweets to the Internet Archive.")
    parser.add_argument("id", help="Twitter ID you want to archive.")
    parser.add_argument('--likecount', type=int, default=0, help="Archive only tweets with more likes than specified number.")
    parser.add_argument('--replycount', type=int, default=0, help="Archive only tweets with more replies than specified number.")
    parser.add_argument('--retweetcount', type=int, default=0, help="Archive only tweets with more retweets than specified number.")
    parser.add_argument('--quotecount', type=int, default=0, help="Archive only tweets with more quotes than specified number.")
    parser.add_argument('--since', default="0001-01-01", help="Archive only tweets after the specified date. yyyy-mm-dd.")
    parser.add_argument('--until', default="9999-12-31", help="Archive only tweets before the specified date. yyyy-mm-dd.")
    parser.add_argument('--nocheck', action="store_false", help="Do not check if archived successfully.")
    parser.add_argument('--debug', action="store_true", help="Display debug logs.")
    args = parser.parse_args()

    if not os.path.isfile(KEYS_PATH):
        with open(KEYS_PATH, mode='x') as f:
            access_key = input("Enter access key: ")
            secret_key = input("Enter secret key: ")
            key_dict = {"access_key":access_key, "secret":secret_key}
            json.dump(key_dict, f)
    with open(KEYS_PATH) as f:
        d = json.load(f)
        access_key = d["access_key"]
        secret = d["secret"]
    
    url_and_jobid_list = []
    url_and_jobid_list = archive_tweet(access_key, secret, args.id, args.likecount, args.replycount, args.retweetcount, args.quotecount, args.debug, args.since, args.until)
    if args.nocheck:
        check_archive(access_key, secret, url_and_jobid_list, args.debug)
    print("Finished")

if __name__ == "__main__":
    main()