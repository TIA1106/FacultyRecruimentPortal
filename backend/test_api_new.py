import requests
import os

BASE_URL = "http://127.0.0.1:5000"

files = ['312b8a08_20200608Reshma.pdf', '05bda005_SureshN.pdf']

for fname in files:
    path = f'd:/Faculty Recruitment Portal/uploads/{fname}'
    print(f"=== Testing API Upload for {fname} ===")
    try:
        with open(path, 'rb') as f:
            resp = requests.post(f"{BASE_URL}/upload", files={'file': (fname, f, 'application/pdf')}, timeout=60)
        
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            pid = data.get('id')
            print(f"ID: {pid}")
            # Try to download PDF
            pdf_resp = requests.get(f"{BASE_URL}/download_pdf?id={pid}")
            print(f"Download Status: {pdf_resp.status_code}")
        else:
            print("Response:", resp.text[:500])
    except Exception as e:
        print(f"Error: {e}")
    print()
