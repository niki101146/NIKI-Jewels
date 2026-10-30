import requests


api_key = "goldapi-482ac7505249a7e36b6e7d7886ca1406-io"

url = "https://www.goldapi.io/api/price/XAU/INR"

headers = {
    "x-access-token": api_key,
    "Content-Type": "application/json",
}

try:

    response = requests.get(
        url,
        headers=headers,
        timeout=10
    )

    print("STATUS:", response.status_code)
    print("RESPONSE:")
    print(response.text)

except requests.exceptions.RequestException as e:

    print("ERROR:", e)