# LibreNMS API scripts

Various Python3 scripts to manipulate data received  
from LibreNMS API.   

## How to
Copy enviroment example and edit it:  
```bash
$ cp .env.example .env
$ vim .env
LIBRENMS_TOKEN="token"
LIBRENMS_URL="https://librenms.mydomain.local"
```
Then create virtual eviroment and run script:  
```bash
$ python3 -m venv ./venv
$ source ./venv/bin/activate
$ pip install -r requirements.txt
$ python3 librenms-api-example.py
```

## License
See [LICENSE](LICENSE).
