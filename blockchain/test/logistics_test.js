const Logistics = artifacts.require("Logistics");

contract("Logistics", (accounts) => {
  it("deploys the contract", async () => {
    const instance = await Logistics.deployed();
    assert.ok(instance.address);
  });

  it("records a shipment and emits an event", async () => {
    const instance = await Logistics.deployed();
    const tx = await instance.recordLogistics("SHIP-001", 12, { from: accounts[0] });
    const count = await instance.getRecordCount();
    assert.equal(count.toString(), "1");
    assert.equal(tx.logs.length, 1);
    assert.equal(tx.logs[0].event, "LogisticsRecorded");
  });

  it("stores shipment id and prediction", async () => {
    const instance = await Logistics.deployed();
    const record = await instance.getRecord(1);
    assert.equal(record.shipmentId, "SHIP-001");
    assert.equal(record.predictedDeliveryHours.toString(), "12");
  });
});
