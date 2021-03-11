import requests

def main():
    target = "134.201.250.155"
    location = get_location(target)
    print("You are in: %s" % location)

def get_location(ip_address):

    api_key = "ef864d79b484fc119c87882e7257cf8b"

    result = requests.get("http://api.ipstack.com/%s?access_key=%s" % (ip_address, api_key))
    data = result.json()
    return "%s, %s" % (data["city"], data["region_code"])

main()