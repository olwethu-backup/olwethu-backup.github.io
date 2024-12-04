// let username = "tiqqun_zoo2"

// const dbName = username + "_wallet"

// console.log("000000" + dbName + "000000")

// const request = indexedDB.open(dbName, 5)
    
//     // .transaction(["zoo"], "readwrite").objectStore("zoo").delete("data")

// request.onsuccess = (event) => {
    
//     const db = request.result
    
//    db.transaction(username).objectStore(username).get(username).onsuccess = (event) => {
//     console.log(`wallet data is ${event.target.result.data.address}`)
// }
//     }
    


// request.onerror = (event) => {
//     console.error("request ERROR!!")
// }

let username = "chuang_red_dust"

const dbName = username + "_wallet"

console.log("000000" + dbName + "000000")

const request = indexedDB.open(dbName, 1)
    
    // .transaction(["zoo"], "readwrite").objectStore("zoo").delete("data")

request.onsuccess = (event) => {
    console.log("----------------><-------]")
    const db = request.result
    console.log(db)
    console.log("TYPEOF(username) = " + typeof(username))
    console.log("username = " + username)


        let transaction = db.transaction([username]);

        
    
        let objectStore = transaction.objectStore(username);
        let request2 = objectStore.get(username);
        request2.onerror = (event) => {
          // Handle errors
            console.error("ERROR IN REQUEST2")
        };
        request2.onsuccess = (event) => {
          // Do something with the request.result!
          console.log(`wallet data is ${request2.result.data.address}`);
        };

    
//    db.transaction("chuang9")
//   .objectStore("chuang9")
//   .get("chuang9").onsuccess = (event) => {
//   console.log(`wallet data is ${event.target.result}`);
// };
//    db.transaction([username]).objectStore(username).get(username).onsuccess = (event) => {
//     console.log(event.target)
//     console.log(`wallet data is ${event.target.result}`)
// }
    }
    


request.onerror = (event) => {
    console.error("request ERROR!!")
}

