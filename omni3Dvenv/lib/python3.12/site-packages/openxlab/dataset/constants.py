README_FILE_NAME = "README.md"
FILE_THRESHOLD = 30 * 1024 * 1024
# FILE_THRESHOLD = 100
# connection timeout and waiting response timeout
TIMEOUT = (5, None)
# max retries when encounter connectionerror
MAX_RETRIES = 3
BASE_DELAY = 1
MAX_DELAY = 32


# # staging
# odl_clientId = 'ypkl8bwo0eb5ao1b96no'
# endpoint = "https://staging.openxlab.org.cn"
# uaa_url_prefix = "https://sso.staging.openxlab.org.cn/gw/uaa-be"

# prod
odl_clientId = "kmz3bkwzlaa3wrq8pvwa"
endpoint = "https://openxlab.org.cn"
uaa_url_prefix = "https://sso.openxlab.org.cn/gw/uaa-be"


computed_url = "/datasets/api/v2/"
