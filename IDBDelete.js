const dbName = "zoo_wallet3"

console.log("000000" + dbName + "000000")

const request = indexedDB.open(dbName, 5)
    
    // .transaction(["zoo"], "readwrite").objectStore("zoo").delete("data")

request.onsuccess = (event) => {
    
    const db = request.result
    
    let request2 = db.transaction(["zoo"], "readwrite").objectStore("zoo").delete("zoo")
    
    request2.onsuccess = (event) => {
        console.log("It's gone!")
    }

    request2.onerror = (event) => {
        console.log("request2 ERROR!!")
    }
    
}

request.onerror = (event) => {
    console.error("request ERROR!!")
}