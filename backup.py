import argparse
import requests
import os
import urllib.parse
from multiprocessing import Pool, freeze_support
from functools import partial

def get(item, args):
    name = item['name']
    dest = "%s/%s" % (args.dest, name)
    if os.path.exists(dest):
        print("%s already exists; skipping." % name)
        return
    print("downloading %s" % name)
    headers = {'Authorization': 'Bearer %s' % args.api_token}
    url = 'https://api.cloudflare.com/client/v4/accounts/%s/storage/kv/namespaces/%s/values/%s'\
        % (args.cf_account_id, args.kv_namespace_id, urllib.parse.quote(name).replace("/", "%2F"))
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        print(f"Failed to download {name}. Status code: {r.status_code}, Response: {r.text}")
        return
    if not os.path.exists(os.path.dirname(dest)):
        os.makedirs(os.path.dirname(dest))
    with open(dest, "wb+") as f:
        f.write(r.content)

def main(args):
    cursor = ""

    if not args.api_token:
        raise Exception("Missing api token")
    if not args.cf_account_id:
        raise Exception("Missing cf account tag")
    if not args.kv_namespace_id:
        raise Exception("Missing kv namespace id")

    if not os.path.exists(args.dest):
        os.makedirs(args.dest)

    pool = Pool(processes=4)

    while True:
        headers = {'Authorization': 'Bearer %s' % args.api_token}
        url = 'https://api.cloudflare.com/client/v4/accounts/%s/storage/kv/namespaces/%s/keys?&cursor=%s'\
                % (args.cf_account_id, args.kv_namespace_id, cursor)
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            print(f"Failed to fetch keys. Status code: {r.status_code}, Response: {r.text}")
            break

        d = r.json()
        print("fetched %d keys" % len(d['result']))

        pool.map(partial(get, args=args), d['result'])

        if d["result_info"]["cursor"]:
            cursor = d["result_info"]["cursor"]
        else:
            break

    pool.close()
    pool.terminate()

if __name__ == '__main__':
    freeze_support()
    
    my_parser = argparse.ArgumentParser(description='List the content of a folder')

    my_parser.add_argument('--api_token', type=str, help='Cloudflare\'s API token')
    my_parser.add_argument('--cf_account_id', type=str, help='Cloudflare\'s account tag')
    my_parser.add_argument('--kv_namespace_id', type=str, help='KV namespace ID')
    my_parser.add_argument('--dest', type=str, help='Dest backup directory', default="./data")

    args = my_parser.parse_args()
    
    main(args)