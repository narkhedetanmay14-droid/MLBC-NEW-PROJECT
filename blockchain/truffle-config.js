const path = require("path");

const rpcUrl = process.env.GANACHE_RPC_URL || "http://127.0.0.1:7545";
const networkId = process.env.GANACHE_NETWORK_ID || "*";

module.exports = {
  contracts_build_directory: path.join(__dirname, "build/contracts"),
  networks: {
    development: {
      host: rpcUrl.replace(/^https?:\/\//, "").split(":")[0],
      port: Number(new URL(rpcUrl).port || 7545),
      network_id: networkId,
      networkCheckTimeout: 10000
    }
  },
  compilers: {
    solc: { version: "0.8.19" }
  }
};
