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

# Page spéciale import.web côté DNS (pour référence, pas utilisée par le navigateur)
DNS["import.web"] = "<!-- Page import.web est intégrée dans le navigateur -->"

# ---------------- Endpoints ----------------
@app.route("/sites", methods=["GET"])
def get_sites():
    # Ne retourne pas import.web pour que le navigateur gère sa version intégrée
    response = {k:v for k,v in DNS.items() if k != "import.web"}
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
    if domain in DNS:
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
        if q in info.get("title","").lower() or q in info.get("description","").lower():
            results.append({"domain":domain,"title":info.get("title"),"description":info.get("description")})
    return jsonify(results)

if __name__ == "__main__":
    port = int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0", port=port)
