# dns_server.py
import os, json
from flask import Flask, request, jsonify

app = Flask(__name__)
DNS_FILE = "dns_data.json"

# Charger ou créer DNS
try:
    with open(DNS_FILE, "r") as f:
        DNS = json.load(f)
except:
    DNS = {}

# Page spéciale import.web toujours disponible
DNS["import.web"] = """
<html>
<head>
<style>
body{background:#282c34;color:white;font-family:Arial;padding:20px;}
h1{color:#00ffff;}
input, select, textarea, button{margin:5px 0;padding:5px;font-size:14px;width:100%;}
#container{max-width:600px;margin:auto;}
button{background:#00ffff;color:#000;border:none;cursor:pointer;}
</style>
</head>
<body>
<div id="container">
<h1>Publier un site</h1>
<p>Nom de domaine : <input id="domain_name" placeholder="ex: mon-site"></p>
<p>Extension :
<select id="domain_ext">
    <option>.web</option><option>.dev</option><option>.fr</option>
    <option>.org</option><option>.test</option><option>.net</option>
</select>
</p>
<p>Code HTML ou URL GitHub : <textarea id="site_content" rows="6" placeholder="Collez HTML ou URL GitHub"></textarea></p>
<p>Description (facultatif) : <textarea id="description" rows="3"></textarea></p>
<button onclick="publish()">Publier</button>
<p id="message" style="color:#ff0;"></p>
</div>

<script>
function publish(){
    fetch('/publish', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({
            domain: document.getElementById("domain_name").value + document.getElementById("domain_ext").value,
            html: document.getElementById("site_content").value,
            title: document.getElementById("domain_name").value,
            description: document.getElementById("description").value
        })
    }).then(r=>r.json()).then(data=>{
        if(data.success){document.getElementById("message").innerText='Site publié !'}
        else{document.getElementById("message").innerText=data.error}
    });
}
</script>
</body>
</html>
"""

# ---------------- Endpoints ----------------
@app.route("/sites", methods=["GET"])
def get_sites():
    # Toujours inclure import.web
    response = DNS.copy()
    response["import.web"] = DNS["import.web"]
    return jsonify(response)

@app.route("/publish", methods=["POST"])
def publish():
    data = request.json
    domain = data.get("domain")
    html = data.get("html")
    title = data.get("title", domain)
    description = data.get("description","")
    if not domain or not html:
        return jsonify({"error":"Domaine ou HTML manquant"}), 400
    if domain in DNS and domain != "import.web":
        return jsonify({"error":"Domaine déjà pris"}), 400
    DNS[domain] = {"html":html,"title":title,"description":description}
    with open(DNS_FILE, "w") as f:
        json.dump(DNS,f)
    return jsonify({"success":True})

@app.route("/search", methods=["GET"])
def search():
    q = request.args.get("q","").lower()
    results = []
    for domain, info in DNS.items():
        if domain == "import.web":
            continue  # Ne pas inclure import.web dans les recherches
        if q in info.get("title","").lower() or q in info.get("description","").lower():
            results.append({"domain":domain,"title":info.get("title"),"description":info.get("description")})
    return jsonify(results)

if __name__ == "__main__":
    port = int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0", port=port)
