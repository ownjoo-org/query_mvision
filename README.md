# query_mvision
Query devices from Trellix mVision

# SECURITY NOTE:
I wrote the .py files.  You have my word that they don't do anything nefarious.  Even so, I recommend that you perform
your own static analysis and supply chain testing before use.  Many libraries are imported that are not in my own control.

# usage
```
$ python query_mvision.py -h
usage: query_mvision.py [-h] --client_id CLIENT_ID --client_secret CLIENT_SECRET --api_key API_KEY [--page_size PAGE_SIZE] [--limit LIMIT] [--proxies PROXIES]

options:
  -h, --help                      show this help message and exit
  --client_id CLIENT_ID           The Client ID for your mVision account
  --client_secret CLIENT_SECRET   The Client Secret for your mVision account
  --api_key API_KEY               The Client Secret for your mVision account
  --page_size PAGE_SIZE           The results page size
  --limit LIMIT                   The results maximum devices limit
  --proxies PROXIES               JSON structure specifying 'http' and 'https' proxy URLs


```

# example
```
$ python query_mvision.py --client_id MyBase64ClientID --client_secret MyClientSecret --api_key MyBase64APIKey --page_size 1 --limit 1
```
