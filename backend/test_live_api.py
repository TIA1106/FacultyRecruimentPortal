import requests
import os
import json

BASE_URL = "http://127.0.0.1:5000"

def test_upload(filepath, label):
    print(f"\n{'='*60}")
    print(f"Testing: {label}")
    print(f"File: {os.path.basename(filepath)}")
    print(f"{'='*60}")
    
    with open(filepath, 'rb') as f:
        files = {'file': (os.path.basename(filepath), f, 'application/pdf')}
        resp = requests.post(f"{BASE_URL}/upload", files=files, timeout=120)
    
    if resp.status_code == 200:
        data = resp.json()
        print(f"Status: OK")
        print(f"Extraction method: {data.get('extraction_method')}")
        d = data.get('data', {})
        print(f"Name: {d.get('name')}")
        print(f"DOB: {d.get('dob')}")
        print(f"Age: {d.get('age')}")
        print(f"Email: {d.get('email')}")
        print(f"Phone: {d.get('phone')}")
        edu = d.get('education', [])
        print(f"Education ({len(edu)} entries):")
        for e in edu[:3]:
            print(f"  - {e}")
        
        profile_id = data.get('id')
        if profile_id:
            pdf_resp = requests.get(f"{BASE_URL}/download_pdf?id={profile_id}", timeout=30)
            if pdf_resp.status_code == 200:
                out_path = f"test_output_{label.replace(' ', '_')}.pdf"
                with open(out_path, 'wb') as out:
                    out.write(pdf_resp.content)
                print(f"PDF downloaded: {out_path} ({len(pdf_resp.content)} bytes)")
            else:
                print(f"PDF download FAILED: {pdf_resp.status_code} - {pdf_resp.text[:200]}")
    else:
        print(f"FAILED: {resp.status_code}")
        print(resp.text[:500])

# Test 1: Scanned PDF (Doc1)
test_upload('d:/Faculty Recruitment Portal/uploads/37f3a6d0_Doc1.pdf', 'Scanned Doc1')

# Test 2: Normal digital PDF (Kavitha - INF010008)
test_upload('d:/Faculty Recruitment Portal/uploads/ede87e0c_INF010008.pdf', 'Normal Kavitha')

print("\nAll tests done!")
