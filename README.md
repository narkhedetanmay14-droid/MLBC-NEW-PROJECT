# Logistics ML Blockchain

A local college-project demonstration combining **Linear Regression**, **Flask**, a plain **HTML/CSS/JavaScript** dashboard, and an **Ethereum-compatible Ganache blockchain** using **Solidity + Truffle**. The ML model predicts delivery time from logistics features; the resulting prediction can then be recorded as an immutable blockchain transaction.

## Objective

The system demonstrates a complete local flow: shipment data is entered in the browser, Flask validates it, the trained Linear Regression model predicts `delivery_time_hours`, and the user can record that prediction on a local Ethereum network.

## Architecture

```text
Frontend (HTML/CSS/Browser JS)
        ↓
Flask Backend
   ├── Linear Regression model
   └── Web3 / Ethereum
            ↓
         Ganache
            ↓
       Logistics.sol
```

## Project structure

```text
Logistics_ML_Blockchain/
├── start.bat
├── requirements.txt
├── README.md
├── .gitignore
├── frontend/index.html
├── frontend/style.css
├── backend/app.py
├── ml/logistics_ml.ipynb
├── data/logistics.csv
├── model/logistics_model.pkl
├── blockchain/contracts/Logistics.sol
├── blockchain/migrations/2_deploy_logistics.js
├── blockchain/test/logistics_test.js
├── blockchain/truffle-config.js
└── blockchain_config.json
```

## Component responsibilities

- `frontend/index.html`: dashboard UI, input form, prediction display, blockchain record action, and status display.
- `frontend/style.css`: responsive visual design.
- `backend/app.py`: backend controller. It validates frontend input, loads the trained model, exposes REST endpoints, and sends blockchain transactions through Web3.
- `ml/logistics_ml.ipynb`: executable ML workflow: load CSV → inspect → preprocess → train Linear Regression → calculate MAE/MSE/RMSE/R² → visualize → export model.
- `data/logistics.csv`: 300-row synthetic logistics training dataset.
- `model/logistics_model.pkl`: trained model bundle containing the model and exact feature order.
- `Logistics.sol`: stores shipment ID, predicted delivery hours, timestamp, and recording account; emits an event.
- `2_deploy_logistics.js`: deploys the contract and automatically updates `blockchain_config.json` with the deployed address.
- `truffle-config.js`: defines the local Ganache development network and Solidity compiler.
- `logistics_test.js`: verifies deployment, record creation, record count, stored values, and event emission.
- `blockchain_config.json`: runtime connection details used by Flask.
- `start.bat`: Windows startup helper. It creates the virtual environment, installs Python requirements, checks Ganache reachability, starts Flask, and opens the browser.

## ML design

Features: `distance_km`, `package_weight_kg`, `traffic_level`, `weather_score`, `vehicle_age_years`, `driver_experience_years`, `warehouse_delay_hours`, `loading_time_hours`, `priority_level`.

Target: `delivery_time_hours`.

The CSV is generated with a mathematical relationship between the features and target plus controlled noise, so Linear Regression has meaningful variation to learn.

Example rows:

```text
distance_km,package_weight_kg,traffic_level,weather_score,vehicle_age_years,driver_experience_years,warehouse_delay_hours,loading_time_hours,priority_level,delivery_time_hours
519.5,1.5,5,4,3,18,3.01,1.27,1,11.65
...
```

## REST API

- `GET /` — serves the frontend.
- `GET /api/health` — reports backend, model, and blockchain status.
- `GET /api/model-info` — returns algorithm, target, and feature order.
- `POST /api/predict` — validates features and returns predicted hours.
- `POST /api/blockchain/record` — records shipment ID and rounded predicted hours on-chain.
- `GET /api/blockchain/status` — checks RPC connectivity, contract address, chain ID, and record count.

## Windows setup

### 1. Python

Verify: `python --version`

Create environment:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Notebook

Run `jupyter notebook`, open `ml/logistics_ml.ipynb`, and run all cells. It writes `model/logistics_model.pkl`. A trained model is included in this generated project as well.

### 3. Ganache Desktop

Install Ganache Desktop, create/open a local Ethereum workspace, and verify the RPC server is listening on `http://127.0.0.1:7545`. Keep Ganache running while the Flask application records transactions. If your workspace uses another port, set the `GANACHE_RPC_URL` environment variable and update `blockchain_config.json`. Use the chain ID shown by your Ganache workspace; the default project value is `1337`.

### 4. Truffle

Verify:

```powershell
node --version
npm --version
truffle version
```

From the `blockchain` folder:

```powershell
cd blockchain
truffle compile
truffle migrate --network development --reset
truffle test
cd ..
```

The migration automatically writes the deployed contract address into `blockchain_config.json`; do not invent or manually type an address.

### 5. Run Flask

```powershell
cd Desktop\Logistics_ML_Blockchain
.venv\Scripts\activate
python backend\app.py
```

Open `http://127.0.0.1:5000`.

### One-click startup

Double-click `start.bat`. It cannot reliably launch Ganache Desktop because the executable path varies. It checks the configured RPC, tells you when Ganache is offline, starts Flask, and opens the browser. Compile/deploy the contract once with Truffle before using blockchain recording.

## Exact startup order

1. Start Ganache.
2. Verify the local RPC.
3. Compile the Solidity contract.
4. Deploy with Truffle.
5. Let the migration update `blockchain_config.json`.
6. Train the ML model through the notebook (or use the included trained model).
7. Start Flask.
8. Open the frontend.
9. Perform a prediction.
10. Record the prediction on blockchain.

## Viva / interview explanation

**What is the project?** A local logistics system that predicts delivery time using Linear Regression and records predictions on an Ethereum-compatible local blockchain.

**Why Machine Learning?** To estimate a numerical logistics outcome from historical/synthetic training data.

**Why Linear Regression?** The target is numerical and the dataset is intentionally designed with approximately linear relationships, making the algorithm simple and explainable for a college project.

**What is a training dataset?** Examples containing input features and a known target used to learn model parameters.

**What is prediction?** Applying the trained model to new feature values to estimate the target.

**What is Flask?** A Python web framework used here to expose HTTP routes and serve the frontend.

**What is a REST API?** HTTP endpoints that allow the browser and backend to exchange structured data, here primarily JSON.

**What is Ethereum?** A programmable blockchain platform based on accounts, transactions, and smart contracts.

**What is Ganache?** A local Ethereum-compatible development blockchain with test accounts.

**What is Solidity?** The smart-contract programming language used for `Logistics.sol`.

**What is a smart contract?** Code deployed on a blockchain whose state-changing functions execute through transactions.

**What is Truffle?** A development framework used here to compile, deploy, and test the Solidity contract.

**Why blockchain?** To demonstrate an appendable transaction record whose state changes are independently verifiable on the local chain.

**How are ML and blockchain integrated?** Flask receives the prediction from the ML model, then Web3 calls the deployed `recordLogistics` contract function with the shipment ID and predicted hours.

**Why store the prediction on blockchain?** To demonstrate an immutable-style transaction record in the local development ledger.

**What is a transaction hash?** The identifier for a blockchain transaction, returned after the transaction is accepted/mined.

**What is an ABI?** The JSON interface describing a deployed contract's callable functions and events so Web3 can interact with it.

**What is a contract address?** The blockchain address at which the deployed `Logistics` contract exists.

**What is an Ethereum account?** An address controlled by a key and used as a sender or recipient; Ganache supplies development accounts.

**Why Ganache instead of mainnet?** It is local, fast, free for development, and uses test accounts rather than real funds.

## Error handling

The backend returns JSON errors for malformed input, missing model/configuration, unavailable Ganache, missing ABI, invalid contract address, unavailable accounts, and failed transactions. The frontend displays these errors rather than Python stack traces.

## Security

No private keys, passwords, API keys, or wallet secrets are stored. Ganache accounts are for local testing only.

## GitHub

Target repository: `narkhedetanmay14-droid/MLBC-REAL-TIME`, default branch `main`. The repository was inspected and is currently empty. The connected GitHub permission is read-only, so this environment cannot honestly push the project. After downloading/copying the project to the Desktop, use:

```powershell
cd Desktop\Logistics_ML_Blockchain
git init
git remote add origin https://github.com/narkhedetanmay14-droid/MLBC-REAL-TIME.git
git branch -M main
git add .
git commit -m "feat: add logistics ML blockchain full-stack project"
git push -u origin main
```

If `origin` already exists, inspect it with `git remote -v` and update it rather than adding a duplicate.

## Validation status

The generated source tree, CSV, notebook, and model were created locally. Python syntax and ML artifacts can be checked in this environment. Ganache deployment, Truffle compilation/tests, Flask runtime dependency installation, browser integration, and Git push require the corresponding local services/software and cannot be truthfully marked successful here without executing them.
