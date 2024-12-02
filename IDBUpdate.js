//update code

let dbName = "zoo_wallet5"

let request = indexedDB.open(dbName, 5)


request.onsuccess = (event) => {
    let db = request.result
    
    let objectStore = db.transaction(["zoo"], "readwrite").objectStore("zoo")
    
    
    let request2 = objectStore.get("zoo")
    
    request2.onerror = (event) => {
        console.error("ERROR IN request2")
    }
    
    request2.onsuccess = (event) => {
        let data = event.target.result
    
        data.data.address = "we changed this shit***"
    
        console.log("data.data.address = " + data.data.address)
        let requestUpdate = objectStore.put(data)
    
        requestUpdate.onerror = (event) => {
            console.error("ERROR IN requestUpdate")
        }
    
        requestUpdate.onsuccess = (event) => {
            console.log("successfully changed wallet content to " + data.data.address)
        }
    
    }
}

request.onerror = (event) => {
    console.error("ERROR IN request")
}
