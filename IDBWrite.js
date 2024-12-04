// This is what our customer data looks like.
let zoo = {"address": "75963c429bd04fe89a8b35f1b52e04af", "password": "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8", "available balance": 0, "pending balance": 0, "total balance": 0, "nodes": ["127.0.0.1:5122", "127.0.0.1:5138", "127.0.0.1:5118", "127.0.0.1:5142", "127.0.0.1:5126", "127.0.0.1:5130", "127.0.0.1:5134"], "port": 5148, "past_transactions": {}}

let customerData = [{"zoo": "zoo", "data": zoo}]

const dbName = "zoo_wallet2"

console.log("000000" + dbName + "000000")

const request = indexedDB.open(dbName, 5);

request.onerror = (event) => {
  // Handle errors.
};
request.onupgradeneeded = (event) => {

  console.log("onupgradeneeded")
  const db = event.target.result;

  // Create an objectStore to hold information about our customers. We're
  // going to use "ssn" as our key path because it's guaranteed to be
  // unique - or at least that's what I was told during the kickoff meeting.
  const objectStore = db.createObjectStore("zoo", { keyPath: "zoo" });


  // Use transaction oncomplete to make sure the objectStore creation is
  // finished before adding data into it.
  objectStore.transaction.oncomplete = (event) => {
    // Store values in the newly created objectStore.
    const customerObjectStore = db
      .transaction("zoo", "readwrite")
      .objectStore("zoo");
    customerData.forEach((zoo_) => {
        console.log("adding " + zoo_["zoo"])
        console.log("zoo = " + zoo_)
        console.log("address = " + zoo_["data"]["address"])
      customerObjectStore.add(zoo_)
    });
  };
};