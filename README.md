# Workers KV backup

Copy the content of a Workers KV locally.

## Usage

```
python3 ./backup.py --api_token=... --cf_account_id=... --kv_namespace_id=...
```

Flags:
- `api_token`: Cloudflare's API token (Permission: Workers KV readonly)
- `cf_account_id`: Cloudflare's Account ID
- `kv_namespace_id`: Workers KV's namespace ID
- `dest`: Optional, backup location (default is `./data`)
