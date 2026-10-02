const Logistics = artifacts.require("Logistics");
const fs = require("fs");
const path = require("path");

module.exports = async function (deployer, network, accounts) {
  await deployer.deploy(Logistics);
  const instance = await Logistics.deployed();
  const rootConfig = path.resolve(__dirname, "../../blockchain_config.json");
  let config = {
    network: "ganache",
    rpc_url: process.env.GANACHE_RPC_URL || "http://127.0.0.1:7545",
    chain_id: 1337,
    contract_address: "",
    contract_name: "Logistics",
    abi_path: "blockchain/build/contracts/Logistics.json"
  };
  if (fs.existsSync(rootConfig)) {
    try { config = { ...config, ...JSON.parse(fs.readFileSync(rootConfig, "utf8")) }; } catch (_) {}
  }
  config.contract_address = instance.address;
  config.chain_id = Number(network === "development" ? (config.chain_id || 1337) : (config.chain_id || 1337));
  config.network = network || "ganache";
  config.rpc_url = process.env.GANACHE_RPC_URL || config.rpc_url;
  fs.writeFileSync(rootConfig, JSON.stringify(config, null, 2) + "\n");
  console.log(`Updated ${rootConfig} with contract address ${instance.address}`);
};
