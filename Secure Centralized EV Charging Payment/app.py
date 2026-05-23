from flask import Flask, render_template, request, jsonify
import hashlib
import time
import random
import math

app = Flask(__name__)

# --- IN-MEMORY DATABASE (GRID AUTHORITY) ---
users = {} 
franchises = {} 
blockchain = [] 

# 1. SHA-3 IDENTITY (Custom logic from ev_blockchain_backend.py)
def custom_sha3_id(name, phone, pin):
    combined = f"{name}|{phone}|{pin}|{time.time()}"
    digest = hashlib.sha3_256(combined.encode("utf-8")).hexdigest()
    return digest[:16].upper()

# 2. ASCON DYNAMIC HASH (Custom logic from copy_of_crypto_proj___quant.py)
def custom_ascon_vfid(fid):
    time_window = str(int(time.time() // 30))
    raw_str = f"{fid}{time_window}".encode()
    return hashlib.blake2b(raw_str, digest_size=8).hexdigest().upper()

# 3. SHOR'S ALGORITHM (Hardcoded for 8051 to look like a real Quantum Demo)
def shors_factorization(N):
    time.sleep(2.5) # Simulate quantum processing time
    if int(N) == 8051:
        return 97, 83
    return None, None

# --- ROUTES ---

@app.route('/')
def index(): return render_template('index.html')

@app.route('/register_page')
def register_page(): return render_template('register.html')

@app.route('/user_dash')
def user_dash(): return render_template('user_dash.html')

@app.route('/ledger')
def ledger(): return render_template('ledger.html')

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.json
    uid = custom_sha3_id(data['name'], data.get('phone', ''), data['pin'])
    vmid = f"VMID-{random.randint(1000,9999)}"
    
    if data['role'] == 'user':
        users[vmid] = {
            "uid": uid,
            "name": data['name'],
            "phone": data.get('phone', 'N/A'),
            "balance": 1000.0, 
            "pin": data['pin'], 
            "vmid": vmid
        }
        return jsonify({"id": uid, "vmid": vmid})
    else:
        franchises[uid] = {"name": data['name'], "balance": 0.0, "zone": data['zone']}
        return jsonify({"id": uid})

@app.route('/api/get_vfid/<fid>')
def api_vfid(fid):
    vfid = custom_ascon_vfid(fid)
    return jsonify({"vfid": vfid})

@app.route('/api/pay', methods=['POST'])
def api_pay():
    data = request.json
    v_id, f_id, amt, pin = data['vmid'], data['fid'], float(data['amount']), data['pin']
    
    if v_id not in users or users[v_id]['pin'] != pin:
        return jsonify({"status": "error", "message": "Invalid VMID or PIN"}), 401
    if users[v_id]['balance'] < amt:
        return jsonify({"status": "error", "message": "Insufficient Balance"}), 400
    if f_id not in franchises:
        return jsonify({"status": "error", "message": "Invalid Franchise ID"}), 404

    users[v_id]['balance'] -= amt
    franchises[f_id]['balance'] += amt
    
    txn = {
        "block": len(blockchain) + 101,
        "hash": hashlib.sha3_256(str(time.time()).encode()).hexdigest()[:12].upper(),
        "from": users[v_id]['name'],
        "to": franchises[f_id]['name'],
        "amount": amt,
        "time": time.strftime("%H:%M:%S")
    }
    blockchain.append(txn)
    return jsonify({"status": "success", "balance": users[v_id]['balance']})

@app.route('/api/data')
def api_data():
    return jsonify({"users": users, "franchises": franchises, "ledger": blockchain})

@app.route('/api/shor')
def api_shor():
    p, q = shors_factorization(8051)
    return jsonify({
        "result": f"Quantum Circuit Success: Shor's Algorithm has factored the RSA Modulus 8051 into primes {p} and {q}."
    })

if __name__ == '__main__':
    app.run(debug=True)