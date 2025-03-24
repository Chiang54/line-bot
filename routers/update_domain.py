import requests

# Cloudflare API 信息
CLOUDFLARE_RECORDS = [
    {
        "api_token": "6tZ_G3KN6z2YznYNDUJq6U0VL_EdGBkMGampk9AX",
        "zone_id": "0c4cea16d6c632cfbe79159ce99bf19c",
        "record_id": "4c993146cd6022f6a8159cd6195ed34f",
        "domain": "cun-rong.com"
    },
    {
        "api_token": "5iBSM5xwIrfqzXiFUZ2oo7KWWpccL9QWFS7w3B63",
        "zone_id": "f3176dc557a7c3f909b074e514ac722d",
        "record_id": "753e4481dfeab724a70903b9f9704d1a",
        "domain": "chiang3693.com"
    }
]
def get_public_ip():
    try:
        return requests.get('http://ipv4.icanhazip.com').text.strip()
    except requests.RequestException as e:
        print(f"Error fetching public IP: {e}")
        return None

def get_dns_record_ip(api_token, zone_id, record_id):
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(url, headers=headers).json()
        return response['result']['content']
    except requests.RequestException as e:
        print(f"Error fetching DNS record: {e}")
        return None

def update_dns_record(api_token, zone_id, record_id, domain, ip):
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    data = {
        "type": "A",
        "name": domain,
        "content": ip,
        "ttl": 1,
        "proxied": True
    }
    try:
        response = requests.put(url, headers=headers, json=data).json()
        return response['success']
    except requests.RequestException as e:
        print(f"Error updating DNS record: {e}")
        return False

if __name__ == '__main__':
    current_ip = get_public_ip()
    if current_ip:
        for record in CLOUDFLARE_RECORDS:
            dns_ip = get_dns_record_ip(record["api_token"], record["zone_id"], record["record_id"])
            if dns_ip and current_ip != dns_ip:
                print(f"Updating Cloudflare DNS for {record['domain']} from {dns_ip} to {current_ip}...")
                if update_dns_record(record["api_token"], record["zone_id"], record["record_id"], record["domain"], current_ip):
                    print(f"DNS for {record['domain']} updated successfully!")
                else:
                    print(f"Failed to update DNS for {record['domain']}.")
            else:
                print(f"No IP change detected for {record['domain']}.")
    else:
        print("Unable to fetch public IP.")