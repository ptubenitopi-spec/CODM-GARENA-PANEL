from flask import Flask, request, jsonify, render_template_string, redirect, session
import psycopg2
import os
import time
import random
import string
import uuid

app = Flask(__name__)
app.secret_key = "slider_super_secure_local_pass_key_12213"

# ==========================================
# DATABASE URL
# ==========================================
DATABASE_URL = os.getenv("DATABASE_URL")

# ==========================================
# ADMIN PASSWORD
# ==========================================
ADMIN_PASSWORD = "Krist12213"
# ==========================================
# FREE KEY LOCK
# ==========================================
FREE_KEY_ENABLED = True

# ==========================================
# DB CONNECTION FIX (IMPORTANT)
# ==========================================
def get_db_connection():
    db_url = os.getenv("DATABASE_URL")

    if not db_url:
        raise Exception("DATABASE_URL is missing in environment variables")

    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    return psycopg2.connect(db_url, sslmode="require")

# ==========================================
# INIT DB (UPDATED FOR DEVICE FINGERPRINT)
# ==========================================
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS free_keys_table (
            license_key TEXT PRIMARY KEY,
            hwid TEXT,
            expiry_timestamp BIGINT,
            game TEXT DEFAULT 'CODM'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blocked_devices (
            hwid TEXT PRIMARY KEY
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS free_tokens (
            token TEXT PRIMARY KEY,
            used BOOLEAN DEFAULT FALSE,
            created_at BIGINT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS device_fingerprints (
            fingerprint TEXT PRIMARY KEY,
            last_claimed BIGINT
        )
    """)

    conn.commit()
    conn.close()
    
# ==========================================
# USER LANDING TEMPLATE (WITH JS FINGERPRINT)
# ==========================================
FREE_LANDING_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Kaze Lider Mods - Registration</title>
<style>
body{background:#ffffff;color:#000000;font-family:sans-serif;padding:20px;margin:0;}
.vip-link{font-size:20px;font-weight:bold;color:#0000ff;text-decoration:underline;display:inline-block;margin-bottom:25px;}
.info-text{font-size:16px;margin-bottom:20px;}
.pricelist-title{font-weight:bold;margin-top:15px;margin-bottom:10px;font-size:18px;}
.price-item{margin:6px 0;font-size:16px;}
.payment-methods{margin-top:15px;font-size:16px;}
.divider{margin:20px 0;color:#5f6368;}
.trial-container{display:flex;align-items:center;justify-content:center;gap:4px;margin-top:35px;flex-wrap:nowrap;}
.tap-here{background:#00a2e8;color:white;font-size:9px;font-weight:bold;padding:4px 12px 4px 6px;text-transform:uppercase;white-space:nowrap;display:inline-block;clip-path: polygon(0% 20%, 75% 20%, 75% 0%, 100% 50%, 75% 100%, 75% 80%, 0% 80%);animation: bounceSolidArrow 0.35s infinite alternate;}
@keyframes bounceSolidArrow{0%{ transform:translateX(0); }100%{ transform:translateX(5px); }}
.trial-link-btn{background:none;border:none;color:#008000;font-size:16px;font-weight:bold;text-decoration:underline;cursor:pointer;white-space:nowrap;padding:0;margin:0;}
.temporary-text{color:#ff0000;font-size:14px;font-weight:bold;white-space:nowrap;margin:0;}
</style>
</head>
<body>
<a href="https://t.me/SliderModMenuCodm" target="_blank" class="vip-link">Purchase VIP, No ads, More features</a>
<div class="info-text">
<div class="pricelist-title">𝘒𝘌𝘠 𝘓𝘖𝘎𝘐𝘕 𝘗𝘙𝘐𝘊𝘌 :</div>
<div class="price-line">-------------------------------------</div>
<div class="price-item">₱150  |  $2.57  •  3 Days</div>
<div class="price-item">₱300  |  $5.15  •  7 Days</div>
<div class="price-item">₱500  |  $8.58  •  15 Days</div>
<div class="price-item">₱730  |  $12.87 •  30 Days</div>
<div class="price-item">₱2,000 | Permanent Access ∞</div>
<div class="payment-methods">GCash • PayPal • Binance • Wise • Telegram Wallet</div>
<div class="payment-methods">𝘈𝘷𝘢𝘪𝘭 𝘕𝘰𝘸: <a href="http://t.me/phia_maganda" target="_blank" style="color:#0088cc;text-decoration:none;font-weight:bold;">𝑷𝒉𝒊𝒂 𝑭𝒆𝒍𝒊𝒄𝒊𝒂</a></div>
</div>
<div class="divider">=======================================</div>
{% if free_enabled %}
<form action="/free/process" method="POST" id="freeForm">
<input type="hidden" name="device_fingerprint" id="deviceFingerprint">
<div class="trial-container">
<div class="tap-here">TAP HERE</div>
<button type="button" onclick="submitFreeForm()" class="trial-link-btn">Free trial link 1.</button>
<span class="temporary-text">(CODM GARENA ONLY)</span>
</div>
</form>
{% else %}
<div style="margin-top:35px;text-align:center;">
<div style="color:red;font-size:28px;font-weight:bold;margin-bottom:20px;">WALA PANG FREE KEY DITO MAG AVAIL KANA LANG!</div>
<div style="font-size:18px;line-height:1.7;">Free trial is currently unavailable.<br>Please wait for free access to reopen<br>OR avail ViP access 🙂</div>
</div>
{% endif %}

<script>
function generateFingerprint() {
    let canvas = document.createElement('canvas');
    let ctx = canvas.getContext('2d');
    ctx.textBaseline = "top";
    ctx.font = "14px 'Arial'";
    ctx.fillText("SliderModDeviceFingerprint", 2, 2);
    let canvasData = canvas.toDataURL();

    let rawData = [
        navigator.userAgent,
        navigator.language,
        screen.colorDepth,
        screen.width + 'x' + screen.height,
        new Date().getTimezoneOffset(),
        navigator.hardwareConcurrency || 'unknown',
        canvasData
    ].join('###');

    let hash = 0;
    for (let i = 0; i < rawData.length; i++) {
        let char = rawData.charCodeAt(i);
        hash = (hash << 5) - hash + char;
        hash |= 0;
    }
    return "fp_" + Math.abs(hash).toString(36) + "_" + screen.width + screen.height;
}

function submitFreeForm() {
    let fp = generateFingerprint();
    document.getElementById('deviceFingerprint').value = fp;
    document.getElementById('freeForm').submit();
}
</script>
</body>
</html>
"""

FREE_GENERATED_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your Free Key</title>
    <style>
        body { background:#ffffff; color:#000000; font-family:sans-serif; padding:20px; text-align:center; }
        .key-container { background:#f3f3f3; padding:15px; border-radius:5px; border:2px dashed #008000; display:inline-block; margin-top:20px; font-size:18px; font-weight:bold; color:#008000; word-break:break-all; }
        .btn-copy { display:inline-block; margin-top:25px; padding:10px 20px; background:#00a2e8; color:white; text-decoration:none; border-radius:5px; font-weight:bold; border:none; cursor:pointer; }
    </style>
</head>
<body>
    <h2>SUCCESSFULLY GENERATED!</h2>
    <p>Join Our Telegram Channel For More Free Update's</p>
    <div class="key-container" id="keyText">{{ key }}</div>
    <br>
    <button class="btn-copy" onclick="copyKey()">Copy Key</button>
    <script>
        function copyKey() {
            var keyElement = document.getElementById("keyText");
            var textArea = document.createElement("textarea");
            textArea.value = keyElement.innerText;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand("copy");
            document.body.removeChild(textArea);
            event.target.innerText = "Copied!";
            setTimeout(function() { event.target.innerText = "Copy Key"; }, 2000);
        }
    </script>
</body>
</html>
"""

ADMIN_LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Login</title>
    <style>
        body { background:#121212; color:white; font-family:Arial; display:flex; justify-content:center; align-items:center; height:100vh; margin:0; }
        .box { background:#1e1e1e; padding:30px; border-radius:10px; width:350px; border:1px solid #333; }
        input,button { width:100%; padding:12px; margin-top:10px; border:none; border-radius:5px; }
        input { background:#2a2a2a; color:white; }
        button { background:#ff3b30; color:white; cursor:pointer; }
        h2 { text-align:center; color:#ff3b30; }
    </style>
</head>
<body>
    <div class="box">
        <h2>GARENA PANEL LOGIN</h2>
        <form method="POST">
            <input type="password" name="password" placeholder="Enter Password" required>
            <button type="submit">Login</button>
        </form>
    </div>
</body>
</html>
"""

ADMIN_PANEL_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Slider Mods - VIP Panel</title>
<style>
body{background:#121212;color:#e0e0e0;font-family:Arial;padding:20px;}
.container{max-width:1000px;margin:auto;}
.card{background:#1e1e1e;padding:20px;border-radius:10px;margin-bottom:20px;border:1px solid #333;}
h1,h2{color:#ff3b30;}
input,select,button{padding:12px;border-radius:5px;border:1px solid #444;font-size:15px;margin-bottom:10px;}
input,select{background:#2a2a2a;color:white;}
button{background:#ff3b30;color:white;border:none;cursor:pointer;}
table{width:100%;border-collapse:collapse;margin-top:15px;}
th,td{border:1px solid #333;padding:12px;text-align:left;}
th{background:#2a2a2a;color:#ff3b30;}
tr:nth-child(even){background:#161616;}
.badge-active{color:#34c759;font-weight:bold;}
.badge-expired{color:#ff3b30;font-weight:bold;}
.badge-nolock{color:#0a84ff;font-weight:bold;}
.badge-mlbb{background:#007aff;color:white;padding:2px 6px;border-radius:3px;font-size:11px;}
.badge-codm{background:#ff9500;color:black;padding:2px 6px;border-radius:3px;font-size:11px;font-weight:bold;}
.btn-reset{background:#ffcc00;color:black;padding:5px 10px;}
.btn-nolock{background:#0a84ff;color:white;padding:5px 10px;}
.btn-delete{background:#8e8e93;color:white;padding:5px 10px;}
.toggle-view-btn{background:#30d158;color:white;padding:10px 15px;border-radius:5px;text-decoration:none;display:inline-block;font-weight:bold;margin-bottom:10px;}
.toggle-view-btn.expired{background:#ff453a;}
.free-status-btn{background:#333;color:white;padding:10px 15px;text-decoration:none;border-radius:5px;font-weight:bold;display:inline-block;margin-bottom:15px;}
</style>
</head>
<body>
<div class="container">

<div style="display:flex;justify-content:space-between;align-items:center;">
<h1>🤖 Slider Mods VIP Dashboard CODM</h1>
<a href="/admin/logout"><button style="background:#ff3b30;color:white;">Logout</button></a>
</div>

<div class="card">
<h2>⚙️ Free Key Control Status</h2>
{% if free_enabled %}
<a href="/admin/free/lock" class="free-status-btn" style="background:#34c759;">🟢 Free Keys Active (Click to Lock)</a>
{% else %}
<a href="/admin/free/unlock" class="free-status-btn" style="background:#ff3b30;">🔴 Free Keys Locked (Click to Unlock)</a>
{% endif %}
</div>

<div class="card">
<h2>🔑 Generate VIP Key</h2>
<form action="/admin/generate_key" method="POST">
<label>Target Game:</label>
<select name="game" style="border: 1px solid #ff3b30;">
    <option value="CODM">Call of Duty Mobile (CODM)</option>
    <option value="MLBB">Mobile Legends (MLBB)</option>
</select>
<br>
<label>Days</label>
<select name="days">
<option value="0">0 Day</option>
{% for i in range(1,31) %}
<option value="{{i}}">{{i}} Day</option>
{% endfor %}
</select>

<label>Hours</label>
<select name="hours">
<option value="0">0 Hour</option>
{% for i in range(1,25) %}
<option value="{{i}}">{{i}} Hour</option>
{% endfor %}
</select>

<label>Minutes</label>
<select name="minutes">
<option value="0">0 Minute</option>
{% for i in range(1,60) %}
<option value="{{i}}">{{i}} Minute</option>
{% endfor %}
</select>
<button type="submit">Generate Random Key</button>
</form>
</div>

<div class="card">
<h2>✏️ Custom Key Generator</h2>
<form action="/admin/custom_generate" method="POST">
<input type="text" name="custom_key" placeholder="Enter Custom Key Name" required style="width:100%;">
<br>
<label>Target Game:</label>
<select name="game" style="border: 1px solid #0a84ff; width:100%;">
    <option value="CODM">Call of Duty Mobile (CODM)</option>
    <option value="MLBB">Mobile Legends (MLBB)</option>
</select>
<br>
<label>Days</label>
<input type="number" name="days" placeholder="Days" value="0" style="width:100%;">
<br>
<label>Hours</label>
<input type="number" name="hours" placeholder="Hours" value="0" style="width:100%;">
<br>
<label>Minutes</label>
<input type="number" name="minutes" placeholder="Minutes" value="0" style="width:100%;">
<br>
<button type="submit" style="background:#0a84ff;">Generate Custom Key</button>
</form>
</div>

<div class="card">
    <h2>🚫 Ban Device</h2>
    <form action="/admin/block_device_manual" method="POST">
        <input type="text" name="hwid" placeholder="Enter Device ID / HWID" required style="width:100%;">
        <button type="submit">Ban This Device</button>
    </form>
</div>

<div class="card">
    <h2>✅ Unban Device</h2>
    <form action="/admin/unblock_device_manual" method="POST">
        <input type="text" name="hwid" placeholder="Enter Device ID / HWID" required style="width:100%;">
        <button type="submit">Unban This Device</button>
    </form>
</div>

<div class="card">
<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
    <h2>🗄️ Database Keys ({% if show_expired %}Expired Keys Logs{% else %}Active Keys Only{% endif %})</h2>
    
    {% if show_expired %}
    <a href="/admin/panel" class="toggle-view-btn">🟢 Show Active Keys</a>
    {% else %}
    <a href="/admin/panel?show_expired=true" class="toggle-view-btn expired">🔴 Show Expired Keys</a>
    {% endif %}
</div>

<input type="text" id="searchInput" placeholder="Search Key or Game..." style="width:100%;padding:12px;margin-top:10px;margin-bottom:15px;background:#2a2a2a;color:white;border:1px solid #444;border-radius:5px;" onkeyup="searchKeys()">
<table>
<thead>
<tr>
<th>License Key</th>
<th>Game</th>
<th>HWID / Status</th>
<th>Expiry Status</th>
<th>Actions</th>
</tr>
</thead>
<tbody>
{% for row in keys %}
<tr>
<td style="font-family:monospace;color:#ffe957;">{{ row[0] }}</td>
<td>
    {% if row[3] == 'CODM' %}
    <span class="badge-codm">CODM</span>
    {% else %}
    <span class="badge-mlbb">MLBB</span>
    {% endif %}
</td>
<td style="font-family:monospace;font-size:12px;color:#aaa;">
{% if row[1] == 'NO_LOCK' %}
<span class="badge-nolock">🔓 Multi-Device (No Lock)</span>
{% elif row[1] %}
{{ row[1] }}
{% else %}
<span style="color:#34c759;">Fresh (Logs first device)</span>
{% endif %}
</td>
<td>
{% if current_time >= row[2] %}
<span class="badge-expired">❌ Expired</span>
{% else %}
<span class="badge-active">✅ Active</span><br>
<small>{{ datetime_format(row[2] )}}</small>
{% endif %}
</td>
<td style="display:flex;gap:5px;flex-wrap:wrap;">
<button type="button" onclick="copyKey('{{ row[0] }}')" style="background:#34c759;color:white;padding:5px 10px;border:none;border-radius:5px;cursor:pointer;">Copy Key</button>
<a href="/admin/reset/{{ row[0] }}?redirect_expired={{ 'true' if show_expired else 'false' }}"><button class="btn-reset">Reset HWID</button></a>
<a href="/admin/nolock/{{ row[0] }}?redirect_expired={{ 'true' if show_expired else 'false' }}"><button class="btn-nolock">No Lock</button></a>
<a href="/admin/edit/{{ row[0] }}?redirect_expired={{ 'true' if show_expired else 'false' }}"><button style="background:#0a84ff;color:white;padding:5px 10px;">Edit Time</button></a>
<a href="/admin/delete/{{ row[0] }}?redirect_expired={{ 'true' if show_expired else 'false' }}"><button class="btn-delete">Delete</button></a>
</td>
</tr>
{% else %}
<tr>
<td colspan="5" style="text-align:center; color:#8e8e93;">No keys found in this section.</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>
</div>

<script>
async function copyKey(key){
    try{
        await navigator.clipboard.writeText(key);
        alert("Copied Key:\\n\\n" + key);
    }catch(err){
        const tempInput = document.createElement("textarea");
        tempInput.value = key;
        document.body.appendChild(tempInput);
        tempInput.select();
        document.execCommand("copy");
        document.body.removeChild(tempInput);
        alert("Copied Key:\\n\\n" + key);
    }
}
function searchKeys(){
    let input = document.getElementById("searchInput");
    let filter = input.value.toUpperCase();
    let table = document.querySelector("table");
    let tr = table.getElementsByTagName("tr");
    for(let i = 1; i < tr.length; i++){
        let tdKey = tr[i].getElementsByTagName("td")[0];
        let tdGame = tr[i].getElementsByTagName("td")[1];
        if(tdKey || tdGame){
            let txtKey = tdKey.textContent || tdKey.innerText;
            let txtGame = tdGame.textContent || tdGame.innerText;
            if(txtKey.toUpperCase().indexOf(filter) > -1 || txtGame.toUpperCase().indexOf(filter) > -1){
                tr[i].style.display = "";
            }else{
                tr[i].style.display = "none";
            }
        }
    }
}
</script>
</body>
</html>
"""

# ==========================================
# USER ROUTES (WITH DEVICE FINGERPRINT COOLDOWN)
# ==========================================
@app.route('/free')
def free_landing():
    return render_template_string(FREE_LANDING_TEMPLATE, free_enabled=FREE_KEY_ENABLED)

@app.route('/free/process', methods=['POST'])
def free_process_route():
    global FREE_KEY_ENABLED
    if not FREE_KEY_ENABLED:
        return '<script>alert("Free Key Locked");window.location="/free";</script>'

    device_fp = request.form.get('device_fingerprint', '').strip()
    if not device_fp:
        return '<script>alert("Invalid Device Signature. Please try again.");window.location="/free";</script>'

    now = int(time.time())
    cooldown_period = 86400  # 24 Oras

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT last_claimed FROM device_fingerprints WHERE fingerprint = %s", (device_fp,))
    result = cursor.fetchone()
    conn.close()

    if result:
        last_claimed = result[0]
        if now - last_claimed < cooldown_period:
            remaining_seconds = cooldown_period - (now - last_claimed)
            rem_hours = int(remaining_seconds / 3600)
            rem_mins = int((remaining_seconds % 3600) / 60)
            rem_secs = int(remaining_seconds % 60)
            return f'<script>alert("This device has already claimed a free trial. Please try again after {rem_hours} hour(s) {rem_mins} minute(s) {rem_secs} second(s).");window.location="/free";</script>'

    token = str(uuid.uuid4())
    session["free_token"] = token
    session["passed_safelink"] = False
    session["device_fp"] = device_fp

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO free_tokens (token, used, created_at) VALUES (%s,%s,%s)", (token, False, now))
    conn.commit()
    conn.close()

    return redirect("https://gplinks.co/FL9tVe")
    
@app.route('/free/return')
def free_return():
    global FREE_KEY_ENABLED
    if not FREE_KEY_ENABLED:
        return '<script>alert("Free Key Locked");window.location="/free";</script>'

    token = session.get("free_token")
    if not token:
        return '<script>alert("Missing Token");window.location="/free";</script>'

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT used FROM free_tokens WHERE token=%s", (token,))
    result = cursor.fetchone()
    conn.close()

    if not result:
        return '<script>alert("Invalid Token");window.location="/free";</script>'
    if result[0]:
        return '<script>alert("Already Used");window.location="/free";</script>'

    session["passed_safelink"] = True
    return redirect("/free/generate/direct")

@app.route('/free/generate/direct')
def free_generate_direct():
    global FREE_KEY_ENABLED
    if not FREE_KEY_ENABLED:
        return '<script>alert("Free Key Locked");window.location="/free";</script>'
    if not session.get("passed_safelink"):
        return '<script>alert("Bypass pa kupal!");window.location="/free";</script>'

    token = session.get("free_token")
    device_fp = session.get("device_fp")
    
    if not token or not device_fp:
        return '<script>alert("Session Expired");window.location="/free";</script>'

    now = int(time.time())
    cooldown_period = 86400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT last_claimed FROM device_fingerprints WHERE fingerprint = %s", (device_fp,))
    result_fp = cursor.fetchone()
    if result_fp and (now - result_fp[0] < cooldown_period):
        remaining_seconds = cooldown_period - (now - result_fp[0])
        rem_hours = int(remaining_seconds / 3600)
        rem_mins = int((remaining_seconds % 3600) / 60)
        rem_secs = int(remaining_seconds % 60)
        conn.close()
        return f'<script>alert("This device has already claimed a free key today. Please try again after {rem_hours} hour(s) {rem_mins} minute(s) {rem_secs} second(s).");window.location="/free";</script>'

    cursor.execute("SELECT used FROM free_tokens WHERE token=%s", (token,))
    token_res = cursor.fetchone()

    if not token_res or token_res[0]:
        conn.close()
        return '<script>alert("Invalid or Used Token");window.location="/free";</script>'

    cursor.execute("UPDATE free_tokens SET used=TRUE WHERE token=%s", (token,))
    
    cursor.execute("""
        INSERT INTO device_fingerprints (fingerprint, last_claimed) 
        VALUES (%s, %s) 
        ON CONFLICT (fingerprint) 
        DO UPDATE SET last_claimed = EXCLUDED.last_claimed
    """, (device_fp, now))

    new_key = "Slider_trial_" + ''.join(random.choices(string.ascii_letters + string.digits, k=13))
    expiry = now + (1 * 3600)

    cursor.execute("INSERT INTO free_keys_table (license_key, hwid, expiry_timestamp, game) VALUES (%s,%s,%s,%s)", (new_key, '', expiry, 'CODM'))
    conn.commit()
    conn.close()

    session.pop("passed_safelink", None)
    session.pop("free_token", None)
    session.pop("device_fp", None)

    return render_template_string(FREE_GENERATED_TEMPLATE, key=new_key)

# ==========================================
# VERIFY API
# ==========================================
@app.route('/verify', methods=['POST'])
def verify_key():
    try:
        key = request.form.get('key', '').strip()
        device_id = request.form.get('device_id', '').strip()
        game = request.form.get('game', '').strip()

        if not key or not device_id:
            return jsonify({"status": 1, "msg": "Missing Parameters"})

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT hwid FROM blocked_devices WHERE hwid = %s", (device_id,))
        if cursor.fetchone():
            conn.close()
            return jsonify({"status": 5, "msg": "Device Blocked"})

        cursor.execute("SELECT hwid, expiry_timestamp, game FROM free_keys_table WHERE license_key = %s", (key,))
        result = cursor.fetchone()

        if not result:
            conn.close()
            return jsonify({"status": 1, "msg": "Invalid Key"})

        saved_hwid, expiry_timestamp, db_game = result
        now = int(time.time())

        if game.upper() != db_game.upper():
            conn.close()
            return jsonify({"status": 4, "msg": f"This key belongs to {db_game} only!"})

        if now >= expiry_timestamp:
            conn.close()
            return jsonify({"status": 3, "msg": "Key Expired"})

        if saved_hwid == 'NO_LOCK':
            conn.close()
            return jsonify({"status": 0, "msg": f"Login Success ({db_game} - No Lock)", "expiry": expiry_timestamp})

        if not saved_hwid:
            cursor.execute("UPDATE free_keys_table SET hwid = %s WHERE license_key = %s", (device_id, key))
            conn.commit()
            saved_hwid = device_id

        if saved_hwid != device_id:
            conn.close()
            return jsonify({"status": 2, "msg": "Key used on another device"})

        conn.close()
        return jsonify({"status": 0, "msg": "Login Success", "expiry": expiry_timestamp})

    except Exception as e:
        return jsonify({"status": 1, "msg": str(e)})
        
# ==========================================
# ADMIN AUTHENTICATION
# ==========================================
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == "POST":
        password = request.form.get("password")
        if password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/admin/panel")
        return "<script>alert('Wrong Password');window.location='/admin/login';</script>"
    return render_template_string(ADMIN_LOGIN_TEMPLATE)

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect("/admin/login")

# ==========================================
# ADMIN PANEL ROUTE
# ==========================================
@app.route('/admin/panel')
def admin_panel():
    if not session.get("admin"):
        return redirect("/admin/login")
        
    show_expired = request.args.get('show_expired', 'false') == 'true'
    now_ts = int(time.time())
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if show_expired:
        cursor.execute("SELECT license_key, hwid, expiry_timestamp, game FROM free_keys_table WHERE expiry_timestamp <= %s ORDER BY expiry_timestamp DESC", (now_ts,))
    else:
        cursor.execute("SELECT license_key, hwid, expiry_timestamp, game FROM free_keys_table WHERE expiry_timestamp > %s ORDER BY expiry_timestamp DESC", (now_ts,))
        
    keys = cursor.fetchall()
    conn.close()

    def datetime_format(timestamp):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))

    return render_template_string(
        ADMIN_PANEL_TEMPLATE, 
        keys=keys, 
        current_time=now_ts, 
        datetime_format=datetime_format, 
        show_expired=show_expired,
        free_enabled=FREE_KEY_ENABLED
    )

# ==========================================
# KEY MANAGEMENT ROUTES
# ==========================================
@app.route('/admin/generate_key', methods=['POST'])
def admin_generate():
    if not session.get("admin"):
        return redirect('/admin/login')

    game_target = request.form.get('game', 'CODM')
    days = int(request.form.get('days', 0))
    hours = int(request.form.get('hours', 0))
    minutes = int(request.form.get('minutes', 0))

    if days == 0 and hours == 0 and minutes == 0:
        return '<script>alert("Enter Time First");window.location.href="/admin/panel";</script>'

    random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=14))
    expiry_seconds = (days * 86400) + (hours * 3600) + (minutes * 60)

    if days > 0:
        prefix = f"Slider_{days}d"
    elif hours > 0:
        prefix = f"Slider_{hours}h"
    else:
        prefix = f"Slider_{minutes}m"

    new_key = prefix + random_str
    expiry_time = int(time.time()) + expiry_seconds

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO free_keys_table (license_key, hwid, expiry_timestamp, game) VALUES (%s, '', %s, %s)", (new_key, expiry_time, game_target))
    conn.commit()
    conn.close()

    return f'<script>alert("Generated {game_target} Key:\\n\\n{new_key}\\n\\nExpiry:\\n{days}D {hours}H {minutes}M");window.location.href="/admin/panel";</script>'

@app.route('/admin/custom_generate', methods=['POST'])
def custom_generate():
    if not session.get("admin"):
        return redirect('/admin/login')

    custom_key = request.form.get('custom_key')
    game_target = request.form.get('game', 'CODM') 
    days = int(request.form.get('days', 0))
    hours = int(request.form.get('hours', 0))
    minutes = int(request.form.get('minutes', 0))

    if not custom_key:
        return '<script>alert("Enter Custom Key");window.location.href="/admin/panel";</script>'

    if days == 0 and hours == 0 and minutes == 0:
        expiry_time = 4102444800
    else:
        expiry_seconds = (days * 86400) + (hours * 3600) + (minutes * 60)
        expiry_time = int(time.time()) + expiry_seconds

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT license_key FROM free_keys_table WHERE license_key = %s", (custom_key,))
        if cursor.fetchone():
            conn.close()
            return '<script>alert("Key Already Exists");window.location.href="/admin/panel";</script>'

        cursor.execute("INSERT INTO free_keys_table (license_key, hwid, expiry_timestamp, game) VALUES (%s, '', %s, %s)", (custom_key, expiry_time, game_target))
        conn.commit()
        conn.close()
        return f'<script>alert("Custom Key Generated for {game_target}\\n\\n{custom_key}");window.location.href="/admin/panel";</script>'
    except Exception as e:
        conn.rollback()
        conn.close()
        return f'<script>alert("Error:\\n\\n{str(e)}");window.location.href="/admin/panel";</script>'

@app.route('/admin/reset/<string:key>', methods=['GET'])
def admin_reset_hwid(key):
    if not session.get("admin"):
        return redirect('/admin/login')

    redirect_target = "/admin/panel?show_expired=true" if request.args.get('redirect_expired') == 'true' else "/admin/panel"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE free_keys_table SET hwid = '' WHERE license_key = %s", (key,))
    conn.commit()
    conn.close()

    return f'<script>alert("HWID Reset Success\\n\\n{key}");window.location.href="{redirect_target}";</script>'

@app.route('/admin/nolock/<string:key>', methods=['GET'])
def admin_no_lock_hwid(key):
    if not session.get("admin"):
        return redirect('/admin/login')

    redirect_target = "/admin/panel?show_expired=true" if request.args.get('redirect_expired') == 'true' else "/admin/panel"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE free_keys_table SET hwid = 'NO_LOCK' WHERE license_key = %s", (key,))
    conn.commit()
    conn.close()

    return f'<script>alert("Key set to NO LOCK (Multi-Device Allowed)\\n\\n{key}");window.location.href="{redirect_target}";</script>'

@app.route('/admin/delete/<string:key>', methods=['GET'])
def admin_delete_key(key):
    if not session.get("admin"):
        return redirect('/admin/login')
        
    redirect_target = "/admin/panel?show_expired=true" if request.args.get('redirect_expired') == 'true' else "/admin/panel"
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM free_keys_table WHERE license_key = %s", (key,))
    conn.commit()
    conn.close()
    return f'<script>alert("Deleted Key\\n\\n{key}");window.location.href="{redirect_target}";</script>'

@app.route('/admin/edit/<string:key>', methods=['GET', 'POST'])
def admin_edit_time(key):
    if not session.get("admin"):
        return redirect('/admin/login')
        
    redirect_target = "/admin/panel?show_expired=true" if request.args.get('redirect_expired') == 'true' else "/admin/panel"
    
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        days = int(request.form.get('days', 0))
        hours = int(request.form.get('hours', 0))
        minutes = int(request.form.get('minutes', 0))
        added_seconds = (days * 86400) + (hours * 3600) + (minutes * 60)
        cursor.execute("SELECT expiry_timestamp FROM free_keys_table WHERE license_key = %s", (key,))
        row = cursor.fetchone()
        if row:
            current_expiry = row[0]
            now = int(time.time())
            new_expiry = (now if current_expiry < now else current_expiry) + added_seconds
            cursor.execute("UPDATE free_keys_table SET expiry_timestamp = %s WHERE license_key = %s", (new_expiry, key))
            conn.commit()
        conn.close()
        return f'<script>alert("Time Updated Successfully");window.location.href="{redirect_target}";</script>'
    conn.close()
    return f'''
    <!DOCTYPE html>
    <html>
    <head><title>Edit Time</title>
    <style>body{{background:#121212;color:white;font-family:Arial;padding:30px;}} .box{{max-width:400px;margin:auto;background:#1e1e1e;padding:20px;border-radius:10px;border:1px solid #333;}} input,button{{width:100%;padding:12px;margin-top:10px;border:none;border-radius:5px;}} input{{background:#2a2a2a;color:white;}} button{{background:#0a84ff;color:white;cursor:pointer;}}</style>
    </head>
    <body><div class="box"><h2>Edit Time</h2><p>{key}</p><form method="POST"><input type="number" name="days" placeholder="Days" value="0"><input type="number" name="hours" placeholder="Hours" value="0"><input type="number" name="minutes" placeholder="Minutes" value="0"><button type="submit">Add Time</button></form></div></body>
    </html>
    '''

@app.route('/admin/block_device_manual', methods=['POST'])
def block_device_manual():
    if not session.get("admin"):
        return redirect('/admin/login')

    hwid = request.form.get('hwid', '').strip()
    if not hwid:
        return '<script>alert("Enter Device ID");window.location.href="/admin/panel";</script>'

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO blocked_devices (hwid) VALUES (%s)", (hwid,))
        conn.commit()
    except Exception:
        conn.rollback()
    conn.close()

    return f'<script>alert("Device Banned\\n\\n{hwid}");window.location.href="/admin/panel";</script>'
    
@app.route('/admin/unblock_device_manual', methods=['POST'])
def unblock_device_manual():
    if not session.get("admin"):
        return redirect('/admin/login')

    hwid = request.form.get('hwid', '').strip()
    if not hwid:
        return '<script>alert("Enter Device ID");window.location.href="/admin/panel";</script>'

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM blocked_devices WHERE hwid = %s", (hwid,))
    conn.commit()
    conn.close()

    return f'<script>alert("Device Unbanned\\n\\n{hwid}");window.location.href="/admin/panel";</script>'

@app.route('/admin/free/lock')
def lock_free_key():
    global FREE_KEY_ENABLED
    if not session.get("admin"):
        return redirect("/admin/login")
    FREE_KEY_ENABLED = False
    return redirect("/admin/panel")

@app.route('/admin/free/unlock')
def unlock_free_key():
    global FREE_KEY_ENABLED
    if not session.get("admin"):
        return redirect("/admin/login")
    FREE_KEY_ENABLED = True
    return redirect("/admin/panel")

# ==========================================
# INIT DB ON START
# ==========================================
init_db()

# ==========================================
# RUN SERVER
# ==========================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
