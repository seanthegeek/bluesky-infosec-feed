import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)
keys = ["infosec_keywords_regex", "infosec_keywords_case_sensitive_regex"]
output = r""
for key in keys:
    value = r.get(key)
    if value:
        output += value
print(output)
