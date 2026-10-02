from pathlib import Path
import json
import re

from flask import Flask, jsonify, request, send_from_directory
import joblib
from web3 import Web3

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"
MODEL_PATH = ROOT / "model" / "logistics_model.pkl"
CONFIG_PATH = ROOT / "blockchain_config.json"

FEATURES = [
    "distance_km", "package_weight_kg", "traffic_level", "weather_score",
    "vehicle_age_years", "driver_experience_years", "warehouse_delay_hours",
    "loading_time_hours", "priority_level"
]

app = Flask(__name__, static_folder=str(FRONTEND), static_url_path="/static")


def load_model_bundle():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"ML model not found: {MODEL_PATH}. Run the notebook first.")
    bundle = joblib.load(MODEL_PATH)
    if isinstance(bundle, dict) and "model" in bundle:
        return bundle["model"], bundle.get("feature_columns", FEATURES)
    return bundle, FEATURES


def load_config():
    if not CONFIG_PATH.exists():
        raise FileNotFoundError("blockchain_config.json is missing")
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def get_contract():
    config = load_config()
    rpc = config.get("rpc_url")
    address = config.get("contract_address")
    abi_path = ROOT / config.get("abi_path", "blockchain/build/contracts/Logistics.json")
    if not rpc:
        raise RuntimeError("Blockchain RPC URL is not configured")
    if not address:
        raise RuntimeError("Contract is not deployed. Run Truffle migration first.")
    if not abi_path.exists():
        raise RuntimeError(f"Contract ABI not found: {abi_path}")
    w3 = Web3(Web3.HTTPProvider(rpc, request_kwargs={"timeout": 5}))
    if not w3.is_connected():
        raise ConnectionError(f"Cannot connect to Ganache at {rpc}")
    try:
        checksum = Web3.to_checksum_address(address)
    except Exception as exc:
        raise ValueError("Invalid contract address in blockchain_config.json") from exc
    artifact = json.loads(abi_path.read_text(encoding="utf-8"))
    return w3, w3.eth.contract(address=checksum, abi=artifact["abi"]), config


def validate_payload(data):
    if not isinstance(data, dict):
        raise ValueError("Request body must be a JSON object")
    values = {}
    for name in FEATURES:
        if name not in data or data[name] in (None, ""):
            raise ValueError(f"Missing feature: {name}")
        try:
            values[name] = float(data[name])
        except (TypeError, ValueError):
            raise ValueError(f"{name} must be numeric")
        if not (-100000 <= values[name] <= 100000):
            raise ValueError(f"{name} is outside the accepted range")
    for name in ("distance_km", "package_weight_kg", "vehicle_age_years", "driver_experience_years", "warehouse_delay_hours", "loading_time_hours"):
        if values[name] < 0:
            raise ValueError(f"{name} cannot be negative")
    for name in ("traffic_level", "weather_score"):
        if not 1 <= values[name] <= 10:
            raise ValueError(f"{name} must be between 1 and 10")
    if not 1 <= values["priority_level"] <= 3:
        raise ValueError("priority_level must be between 1 and 3")
    return values


@app.get("/")
def index():
    return send_from_directory(FRONTEND, "index.html")


@app.get("/api/health")
def health():
    result = {"success": True, "backend": "online", "model": False, "blockchain": False, "messages": []}
    try:
        load_model_bundle(); result["model"] = True
    except Exception as exc:
        result["messages"].append(str(exc))
    try:
        get_contract(); result["blockchain"] = True
    except Exception as exc:
        result["messages"].append(str(exc))
    result["success"] = result["model"] and result["blockchain"]
    return jsonify(result)


@app.get("/api/model-info")
def model_info():
    try:
        _, feature_order = load_model_bundle()
        return jsonify({"success": True, "model": "Linear Regression", "target": "delivery_time_hours", "features": feature_order})
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


@app.post("/api/predict")
def predict():
    try:
        values = validate_payload(request.get_json(silent=True))
        model, feature_order = load_model_bundle()
        prediction = float(model.predict([[values[f] for f in feature_order]])[0])
        return jsonify({"success": True, "prediction_hours": round(max(0.0, prediction), 2), "model": "Linear Regression"})
    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


@app.post("/api/blockchain/record")
def record():
    try:
        data = request.get_json(silent=True) or {}
        shipment_id = str(data.get("shipment_id", "")).strip()
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", shipment_id):
            raise ValueError("shipment_id must be 1-64 characters using letters, numbers, _ or -")
        prediction = float(data.get("prediction_hours"))
        if not 0 <= prediction <= 100000:
            raise ValueError("prediction_hours is outside the accepted range")
        w3, contract, config = get_contract()
        accounts = w3.eth.accounts
        if not accounts:
            raise RuntimeError("Ganache returned no available accounts")
        sender = accounts[0]
        tx = contract.functions.recordLogistics(shipment_id, int(round(prediction))).transact({"from": sender})
        receipt = w3.eth.wait_for_transaction_receipt(tx, timeout=30)
        return jsonify({"success": True, "transaction_hash": receipt["transactionHash"].hex(), "block_number": receipt["blockNumber"], "contract_address": config["contract_address"]})
    except (ValueError, TypeError) as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 503


@app.get("/api/blockchain/status")
def blockchain_status():
    try:
        w3, contract, config = get_contract()
        count = contract.functions.getRecordCount().call()
        return jsonify({"success": True, "connected": True, "network": config.get("network"), "rpc_url": config.get("rpc_url"), "chain_id": w3.eth.chain_id, "contract_address": config.get("contract_address"), "record_count": count})
    except Exception as exc:
        return jsonify({"success": False, "connected": False, "error": str(exc)}), 503


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
