const dbName = "zoo_wallet5"

console.log("000000" + dbName + "000000")

const request = indexedDB.open(dbName, 5)
    
    // .transaction(["zoo"], "readwrite").objectStore("zoo").delete("data")

request.onsuccess = (event) => {
    
    const db = request.result
    
   db.transaction("zoo").objectStore("zoo").get("zoo").onsuccess = (event) => {
    console.log(`zoo data is ${event.target.result.data.address}`)
}
    }
    


request.onerror = (event) => {
    console.error("request ERROR!!")
}
