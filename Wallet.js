function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}



class Wallet{

    //Javascript port of blockchain_wallet.py

    constructor(){
        this.username = ''

        this.address = uuidv4().replaceAll("-", "")
        this.available = 0
        this.pending = 0
        this.total = this.available + this.pending
        this.nodes = new Set()
        this.port = -1
        this.pastTransactions = new Map()

    }

    createWalletFile(username){

        

        let walletTemplate = {"address": "placeholder", "password": "placeholder", "available balance": 0, "pending balance": 0, "total balance": 0, "nodes": [], "port": -1, "past_transactions": {}}
       
       //---------------UNCOMMENT
        // let walletData = {}
        // walletData[username] = "placeholder"
        // walletData["data"] = walletTemplate
        // let totalWalletData = [walletData]
    // ---------------UNCOMMENT

        let totalWalletData = [{"username": username, "data": walletTemplate}]


        //---------------COMMENT WHEN FINISHED
        // let totalWalletData = [{"chuang3": "placeholder", "data": walletTemplate}]
        //---------------COMMENT WHEN FINISHED


        // let walletData = [{"" + `${username}` : "placeholder", "data": walletTemplate}]




        let dbName = username + "_wallet"

        console.log("000000" + dbName + "000000")

        let request = indexedDB.open(dbName, 1);

        request.onerror = (event) => {
            console.error("Error in request in createWalletFile")
        };

        request.onupgradeneeded = (event) => {

            console.log("onupgradeneeded")
          const db = event.target.result;
        
          // Create an objectStore to hold information about our customers. We're
          // going to use "ssn" as our key path because it's guaranteed to be
          // unique - or at least that's what I was told during the kickoff meeting.
          console.log("typeof(username) 1 = " + typeof(username))
          const objectStore = db.createObjectStore(username, { keyPath: "username" });
        
                          
          // Use transaction oncomplete to make sure the objectStore creation is
          // finished before adding data into it.
          objectStore.transaction.oncomplete = (event) => {
            // Store values in the newly created objectStore.

            console.log("typeof(username) 2 = " + typeof(username))
            const walletObjectStore = db
              .transaction(username, "readwrite")
              .objectStore(username);

            console.log("typeof(username) 3 = " + typeof(username))
            totalWalletData.forEach((wallet_) => {
                console.log("typeof(username) 4 = " + typeof(username))
                console.log("adding " + wallet_["username"])
                console.log("wallet = " + wallet_)
                console.log("address = " + wallet_["data"]["address"])
              walletObjectStore.add(wallet_)
            });
          };
        };






    }

    saveTransaction(transactionMap){
        console.log("transactionMap [saveTransaction()] = " + transactionMap)

        for (var [key, value] of transactionMap){
            console.log(key + " => " + value)
        }


        this.updateFile("past_transactions", Object.fromEntries(transactionMap))
        console.log("Object.fromEntries(transactionMap) = " + Object.fromEntries(transactionMap))

    }



    updateFileMultipleFields(dataMap, theUsername = ""){
        

        let walletStr= ""
        let walletDict = ""
        if (theUsername == ""){
            theUsername = this.username
        }
        
        // let myUUID = uuidv4().replaceAll("-", "")
        // console.log("UUID = " + myUUID)

        let dbName = theUsername + "_wallet"

        let request = indexedDB.open(dbName, 1)


        request.onsuccess = (event) => {

        let db = request.result

        let objectStore = db.transaction([theUsername], "readwrite").objectStore(theUsername)

        // let request2 = objectStore.get("username")

        


     

        let request2 = objectStore.get(theUsername)

        request2.onerror = (event) => {
            console.error("ERROR IN request2")
        }
    
        

        request2.onsuccess = (event) => {
            
            console.log("this.username (updateFile) = " + theUsername)
            

            let data = event.target.result



            for (var [key, value] of dataMap){
                console.log("###############" + key + "###############")
                data.data[key] = value
                console.log("data.data[" + key + "] = " + value)
            }

            let requestUpdate = objectStore.put(data)

            requestUpdate.onerror = (event) => {
                console.error("ERROR IN requestUpdate")
            }
        
            requestUpdate.onsuccess = (event) => {
                console.log("successfully changed wallet content to " + data.data)
            }      

            console.log("done!!!!!!!!")
        }
    }

    request.onerror = (event) => {
        console.error("ERROR IN request")
    }

      
    }

    updateFile(field, newData, theUsername = ""){
        
        
        // let myUUID = uuidv4().replaceAll("-", "")
        // console.log("UUID = " + myUUID)



        let walletStr= ""
        let walletDict = ""
        if (theUsername == ""){
            theUsername = this.username
        }

        let dbName = theUsername + "_wallet"

        let request = indexedDB.open(dbName, 1)


        request.onsuccess = (event) => {
            console.log("###############" + field + "###############")
            console.log("this.username (updateFile) = " + theUsername)
            // console.log('err = ' + err)

            let db = request.result
    
            let objectStore = db.transaction([theUsername], "readwrite").objectStore(theUsername)
            
            
            let request2 = objectStore.get(theUsername)

            request2.onsuccess = (event) => {
                let data = event.target.result
            

                console.log(`data.data[${field}] old = ` + data.data[field])

                data.data[field] = newData
            
                console.log(`data.data[${field}] new = ` + data.data[field])
                let requestUpdate = objectStore.put(data)
            
                requestUpdate.onerror = (event) => {
                    console.error("ERROR IN requestUpdate")
                }
            
                requestUpdate.onsuccess = (event) => {
                    console.log("successfully changed wallet content to " + data.data[field])
                }
            
            }
        


            
            console.log("done")
        }
      
    }



    saveTransactions(){

        let walletStr= ""
        let walletDict = ""

        this.updateFile("past_transactions", Object.fromEntries(this.pastTransactions))


      
    }

   async registerNode(nodes){
        // let sleepMs = 10000

        // console.log("(loginOffline) Sleeping for " + sleepMs + "ms...")
        // await sleep(sleepMs)
        // console.log("(loginOffline) Done sleeping")
        this.nodes = new Set(nodes);
        this.updateFile("nodes", nodes)

        console.log("nodes successfully registered")
        console.log("nodes = " + nodes)


    }


    async send(address, amount){


        // console.log("[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[")
        await this.updateBalance()
        // console.log("[](send)\n[](send)\n[](send)\n[](send)\n[](send)\n[](send)\n[](send)\n[](send)\n[](send)\n[](send)\n[](send)\n[](send)\n")

        // console.log("this.available=" + this.available)
        
        
        


        let valuesObject = {
            "recipient": address,
            "amount": amount
        }

        valuesObject["transaction_id"] = uuidv4().replaceAll("-", "")
        valuesObject["sender"] = this.address
        valuesObject["status"] = "pending"


        let valuesDict = new Map(Object.entries(valuesObject))

        // console.log("valuesObject = " + valuesObject)
        // console.log("valuesDict = " + valuesDict)

        // for (var [key, value] of valuesDict){
        //     console.log(key + " => " + value)
        // }


        if (amount > this.available){
            console.log("Requested amount (" + amount + ") exceeds available balance (" + this.available + ").")
            return "Requested amount (" + amount + ") exceeds available balance (" + this.available + ")."
        }
        if (amount < 0){
            console.log("Requested amount (" + amount + ") is less than zero.")
            return "Requested amount (" + amount + ") is less than zero."
        }


        let response = {
            "message": 'successful test',
            "values": valuesDict

        }


        this.pastTransactions.set(valuesDict.get("transaction_id"), valuesDict)
        console.log("valuesDict [send()] = " + valuesDict)
        this.saveTransaction(valuesDict)

        console.log("this.nodes=" + this.nodes)

        let nodeResponses = await this.asyncRequest("/propagate", valuesObject)

        console.log("**********************************************************")
        console.log('nodeResponses=' + nodeResponses)
        console.log("**********************************************************")


        // console.log("[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[")

        this.available -= amount
        this.pending += amount

        this.total = this.available + this.pending


        console.log(response['message'])
        console.log('\n\n')
        console.log(response['values'])







    }

    readChain(chain){
        let transactionAddress = this.address

        console.log("transactionAddress=" + transactionAddress)

        let available = 0
        let transactionRecentlyConfirmed = false

        console.log("chain.length=" + chain.length)

        let blockNum = 0
        let transaction = {}
        let block = {}

        for (let i = 0; i < chain.length; i++) {
           console.log("blockNum=" + blockNum)

           block = chain[i]
           blockNum += 1

           for (let j = 0; j < block["transactions"].length; j++){
                console.log("[[[[blockNum=" + blockNum + "]]]]")

                transaction = block["transactions"][j]

                console.log()
                console.log("transaction['sender']=" + transaction['sender'])
                console.log("transaction['recipient']=" + transaction['recipient'])
                console.log("transaction['transaction_id']=" + transaction['transaction_id'])
                console.log("transaction['amount']=" + transaction['amount'])
                console.log()


                if (transaction['sender'] == transactionAddress){

                    if(this.pastTransactions.has(transaction["transaction_id"])){
                        if (this.pastTransactions.get(transaction["transaction_id"])["status"] == "pending"){
                            this.pastTransactions.get(transaction["transaction_id"]).set("status", "confirmed")
                        }
                        if (!transactionRecentlyConfirmed){
                            transactionRecentlyConfirmed = true
                        }
                    }

                    available -= parseFloat(transaction["amount"])

                    console.log("sender")
                    console.log("parseFloat(transaction['amount'])=" + parseFloat(transaction['amount']))
                    console.log("available=" + available)
                    console.log(".................")
                }

                if (transaction["recipient"] == transactionAddress){
                    if (this.pastTransactions.has(transaction["transaction_id"])){
                        if (this.pastTransactions.get(transaction["transaction_id"])["status"] == "pending"){
                            this.pastTransactions.get(transaction["transaction_id"]).set("status", "confirmed")
                        }

                        if (!transactionRecentlyConfirmed){
                            transactionRecentlyConfirmed = true
                        }
                    }

                    available += parseFloat(transaction["amount"])

                    console.log("recipient")
                    console.log("parseFloat(transaction['amount'])=" + parseFloat(transaction['amount']))
                    console.log("available=" + available)
                    console.log(".................")
                }
           }
            
        }

        // console.log("this.available=" + this.available)

        this.available = available

        console.log("this.available=" + this.available)


        if (transactionRecentlyConfirmed){
            this.saveTransactions()
        }
        




        


    }

    async getBlockchain(){

        console.log("(getBlockchain) this.nodes=" + this.nodes)
        console.log("(getBlockchain) this.nodes.size=" + this.nodes.size)
        console.log(" (getBlockchain) this.nodes.values()=" + this.nodes.values())        
        
        if (this.nodes.size == 0){
            console.log("(getBlockchain) this.nodes.size == 0")
            console.log("(getBlockchain) No available nodes to get blockchain data from. Register some nodes to be able to update your balance.")    
            return
        }

        if (this.nodes.size < 0){
            console.log("(getBlockchain) this.nodes.size < 0 (HOW?!?!??!)")
            return
        }

        


        

        let urls = []

        let nodesIterator = this.nodes.values()

        let node = ""

        let protocol = "https"
        
        for (let n = 0; n < this.nodes.size; n++){

            node = nodesIterator.next().value

            // console.log("node=" + node)

            if (node[0] == "1"){
                protocol = "http"
            }

            urls.push(axios.get(protocol + "://" + node + "/chain").catch(function(error){
                console.log(node + " is unavailable~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                
                if (error.response) {
                    // The request was made and the server responded with a status code
                    // that falls out of the range of 2xx
                    // console.log(error.response.data);
                    // console.log(error.response.status);
                    // console.log(error.response.headers);

                    console.log("(getBlockchain) ~~~~~~~~~~~")

                  } else if (error.request) {
                    // The request was made but no response was received
                    // `error.request` is an instance of XMLHttpRequest in the browser and an instance of
                    // http.ClientRequest in node.js
                    // console.log(error.request);

                    console.log("(getBlockchain) &&&&&&&&&&&")
                  } else {
                    // Something happened in setting up the request that triggered an Error
                    // console.log('Error', error.message);
                    console.log("(getBlockchain) %%%%%%%%%%%")
                    
                  }
            }))

            
        }

       let theChain = await axios.all(urls).then(axios.spread((...responses) =>{


                console.log("responses = " + responses)
                let response = responses[0] //TODO: modify this to seek the longest chain that was provided
        
                console.log("response = " + response)
                console.log("status=" + response["status"])
                console.log("status type: " + typeof(response["status"]))
        
                // let sleepMs = 1500
        
                // console.log("(getBlockchain) Sleeping for " + sleepMs + "ms...")
                // await sleep(sleepMs)
                // console.log("(getBlockchain) Done sleeping")
        
        
                if (response["status"] == 200){
                    let length = response["data"]["length"]
                    let chain = response["data"]["chain"]
        
                    console.log("chain (getBlockchain) =")
                    console.log(chain)
                    return chain
                }
 


            
            // return responses


       })).catch(errors => {
        console.error(errors)
       })

       return theChain

    
   

    }

    async updateBalance(){
        console.log("this.nodes=" + this.nodes)
        console.log("this.nodes.size=" + this.nodes.size)
        console.log("this.nodes.values()=" + this.nodes.values())        
        
        if (this.nodes.size == 0){
            console.log("this.nodes.size == 0")
            console.log("No available nodes to get blockchain data from. Register some nodes to be able to update your balance.")    
            return
        }

        if (this.nodes.size < 0){
            console.log("this.nodes.size < 0 (HOW?!?!??!)")
            return
        }

        


        

        let urls = []

        let nodesIterator = this.nodes.values()

        let node = ""

        let protocol = "https"
        
        for (let n = 0; n < this.nodes.size; n++){

            node = nodesIterator.next().value

            // console.log("node=" + node)

            if (node[0] == "1"){
                protocol = "http"
            }

            urls.push(axios.get(protocol + "://" + node + "/chain").catch(function(error){
                console.log(node + " is unavailable~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                
                if (error.response) {
                    // The request was made and the server responded with a status code
                    // that falls out of the range of 2xx
                    // console.log(error.response.data);
                    // console.log(error.response.status);
                    // console.log(error.response.headers);

                    console.log("~~~~~~~~~~~")

                  } else if (error.request) {
                    // The request was made but no response was received
                    // `error.request` is an instance of XMLHttpRequest in the browser and an instance of
                    // http.ClientRequest in node.js
                    // console.log(error.request);

                    console.log("&&&&&&&&&&&")
                  } else {
                    // Something happened in setting up the request that triggered an Error
                    // console.log('Error', error.message);
                    console.log("%%%%%%%%%%%")
                    
                  }
            })
            )

            
        }

       let theBalance = await axios.all(urls).then(axios.spread((...responses) =>{

        console.log("responses = " + responses)
        let response = responses[0] //TODO: modify this to seek the longest chain that was provided
 
        console.log("response = " + response)
        console.log("status=" + response["status"])
        console.log("status type: " + typeof(response["status"]))
 
      
 
 
        if (response["status"] == 200){
             let length = response["data"]["length"]
             let chain = response["data"]["chain"]
 
             console.log("chain (updateBalance) =")
             console.log(chain)
 
             this.readChain(chain)
 
             this.total = this.available + this.pending
 
             let pending = 0
 
             for (var [key, value] of this.pastTransactions){
                 console.log("-----------------------------------")
                 if (this.pastTransactions.get(key)["status"] == "pending"){
                        pending += parseFloat(this.pastTransactions.get(key)["amount"])
                        console.log("FOUND PENDING TRANSACTION: " + key + "\nAMOUNT:" + parseFloat(this.pastTransactions.get(key)['amount']) + "\nPENDING: " + pending)                 
                 } 
 
             }
 
             this.pending = pending
             this.total = this.available + this.pending
 
             console.log("____________________________________available balance")
             this.updateFile("available balance", this.available)
             console.log("____________________________________pending balance")
             this.updateFile("pending balance", this.pending)
             console.log("____________________________________total balance")
             this.updateFile("total balance", this.total)
             //TODO: test that this works (IMPORTANT)
 
        }

            
    


       })).catch(errors => {
        console.log("*************************")
        console.log("---------------------------------------")
        console.error(errors)
        console.log("---------------------------------------")
        console.log("*************************")
       })

    //    console.log("theResponses=" + theResponses)
    //    for (let q = 0; q < theResponses.length; q++){
    //     console.log("]" + q + "[")
    //     console.log(theResponses[q])

    //    }         

       










       

       

        

    }
    
    async requestTest(){
        let theResponse = await fetch("http://127.0.0.1:5122/chain", 
                {
                    method: 'GET'
                }
        ).then(
            response => {
                // console.log("response")
                // console.log(response)
                // console.log("response.json()")
                // console.log(response.json())
                // console.log("response['body']")
                // console.log(response["body"])
                return response.json()
            },
            rejection => {
                console.error(rejection.message)
            }
        )


        console.log("////theResponse////")
        console.log(theResponse)
        
    }



    async asyncRequest(endpoint, parameters){

        let urls = []
        console.log("-1-")
        console.log("this.nodes.size=" + this.nodes.size)

        let nodesIterator = this.nodes.values()

        let node = ""

        let protocol = "https"
        

        for (let i = 0; i < this.nodes.size; i++){

           
            node = nodesIterator.next().value

            
            if (node[0] == "1"){
                protocol = "http"
            }

            console.log("NODE = " + node)
            console.log("))))))))))))))))))))))))))))))))))))))))))))))")
            urls.push(axios.get(protocol + "://" + node + endpoint, {params: parameters}))
        }

        console.log("-2-")
        console.log("urls.length=" + urls.length)
        console.log("urls=" + urls)

        for (let j = 0; j < urls.length; j++){
            console.log(urls[j])
        }
        console.log("-3-")


        
        let theResponses = await axios.all(urls).then(axios.spread((...responses) => {

            console.log('responses.length=' + responses.length)
            for (let r = 0; r < responses.length; r++){
                console.log('--------------')
                console.log(responses[r])
                console.log('||||||||||||||')
          
            }

            console.log("______________________________________")

            console.log("RESPONSES = " + responses)
            
            console.log("______________________________________")

            return responses
            


        
        })).catch(errors => {
            console.error(errors)
        })
        
        console.log("/////////////////////////////////////////")
        console.log("theResponses = ")
        console.log(theResponses)
        for (let k = 0; k < theResponses.length; k++){
            console.log("["+k+"]")
            console.log(theResponses[k]["data"])
            console.log("___________________________________________")
        }

        return theResponses

    }

    async requestMapTest(){

        let urls = []
        console.log("-1-")
        console.log("this.nodes.size=" + this.nodes.size)

        let nodesIterator = this.nodes.values()

        let node = ""

        let address = "test"
        let amount = 0

        let protocol = "https"

        for (let i = 0; i < this.nodes.size; i++){
            node = nodesIterator.next().value

            
            if (node[0] == "1"){
                protocol = "http"
            }

            urls.push(axios.get(protocol + "://" + node + "/propagate", {params: {
                "recipient": address,
                "amount": amount
            }}))
        }

        console.log("-2-")
        console.log("urls.length=" + urls.length)
        console.log("urls=" + urls)

        for (let j = 0; j < urls.length; j++){
            console.log(urls[j])
        }
        console.log("-3-")


        
        let theResponses = await axios.all(urls).then(axios.spread((...responses) => {

            console.log('responses.length=' + responses.length)
            for (let r = 0; r < responses.length; r++){
                console.log('--------------')
                console.log(responses[r])
                console.log('||||||||||||||')
          
            }
            
            return responses
            


        
        })).catch(errors => {
            console.error(errors)
        })
        
        console.log("/////////////////////////////////////////")
        console.log("theResponses")
        for (let k = 0; k < theResponses.length; k++){
            console.log("["+k+"]")
            console.log(theResponses[k]["data"])
            console.log("___________________________________________")
        }

    
        
    }

}




let wallet = new Wallet()












function registerOffline(username = "", password = ""){

        // Receives a username and password, will automatically generate an address for this account.
    
        console.log("\n\n")
        console.log("============REGISTER============")
        console.log("\n\n")
    
        // const rl = readline.createInterface({
        //     input: process.stdin,
        //     output: process.stdout,
        // })
    
        // if (username == "" && password == ""){
        //     username = rl.question(`username: `, name => {
        //         console.log("name = " + name)
        //         console.log("question was answered")
        //         rl.close()
        //         return name
        //     })
    
            // username = "graeber"
            // password = "password"
            
            console.log("password = " + password)
    
            let passwordBitArray = sjcl.hash.sha256.hash(password)
            
            console.log("passwordBitArray = " + passwordBitArray)
    
            
            let passwordHash = sjcl.codec.hex.fromBits(passwordBitArray)
    
            console.log("passwordHash = " + passwordHash)
    
            let walletInfo = {
                "username": username,
                "port": -1, //TODO: Dedicated port is no longer necessary
                "password": passwordHash,
                "address": uuidv4().replaceAll("-", ""),
                "available balance": 0,
                "pending balance": 0,
                "total balance": 0,
                "nodes": [],
                "past_transactions": {}
            }
    
            wallet.createWalletFile(username)
    
        //     let sleepMs = 10000
    
        //    console.log("(updateBalance) Sleeping for " + sleepMs + "ms...")
        //    await sleep(sleepMs)
        //    console.log("(updateBalance) Done sleeping")
    
            let walletMap = new Map(Object.entries(walletInfo))
    
            wallet.updateFileMultipleFields(walletMap, username)
    
           
            let response = {
                "message": "Wallet " + walletInfo["username"] + " created",
                "address": walletInfo["address"]
            }
    
            console.log(response["message"])
            console.log("address: " + response["address"])
    
            // console.log("typeof(passwordHash) = " + typeof(passwordHash))
            
    
            
    
            // console.log("username = " + username)
    
            // password = prompt("password: ")
    
    
            
        }
    











async function loginOffline(username = "", password = "", encrypted = false){
    let walletStr = ""
    let walletDict = ""
    
   

    const dbName = username + "_wallet"

    console.log("000000" + dbName + "000000")

    const request = await indexedDB.open(dbName, 1)



    request.onsuccess = (event) => {

        console.log("event.target.result = " + event.target.result)
        
        let passwordHash = password //in the event where the password was already encrypted by the login page
        
        let db = event.target.result

        console.log("db = " + db)

        console.log("password = " + password)


        if (!encrypted){
        

        let passwordBitArray = sjcl.hash.sha256.hash(password)
        
        console.log("passwordBitArray = " + passwordBitArray)
    
        
        passwordHash = sjcl.codec.hex.fromBits(passwordBitArray)
        console.log("passwordHash = " + passwordHash)


    }else{
        console.log("passwordHash (encrypted = true) = " + passwordHash)
    }
        



        console.log("----------------><-------]")
        
        console.log()
        
        console.log(db)
        console.log("TYPEOF(username) = " + typeof(username))
        console.log("username = " + username)



            console.log("db.address = " + db.address)


            
            let transaction = db.transaction(username)
            let objectStore = transaction.objectStore(username)
            let request2 = objectStore.get(username)

            request2.onerror = (event) => {
                  // Handle errors
                    console.error("ERROR IN REQUEST2 in loginOffline()") 
                };
                
                request2.onsuccess = (event) => {
                  // Do something with the request.result!
    
                  console.log(`wallet encrypted password is ${request2.result.data.password}`);

                  if (passwordHash != request2.result.data.password){
                    console.log("username or password is incorrect")


                                
                }

                else{
                    console.log("username and password are correct")

                    wallet.username = username
                    console.log(`[wallet.username] = ${username}`)
                    wallet.port = request2.result.data.port
                    console.log(`[wallet.port] = ${request2.result.data.port}`)
                    wallet.address = request2.result.data.address
                    console.log(`[wallet.address] = ${request2.result.data.address}`)
                    wallet.available = request2.result.data["available balance"]
                    console.log(`[wallet.available] = ${request2.result.data["available balance"]}`)
                    wallet.pending = request2.result.data["pending balance"]
                    console.log(`[wallet.pending] = ${request2.result.data["pending balance"]}`)
                    wallet.total = request2.result.data["total balance"]
                    console.log(`[wallet.total] = ${request2.result.data["total balance"]}`)
                    wallet.nodes = new Set(request2.result.data.nodes)
                    console.log(`[wallet.nodes] = ${new Set(request2.result.data.nodes)}`)
                    wallet.pastTransactions = new Map(Object.entries(request2.result.data.past_transactions))
                    console.log(`[wallet.pastTransactions] = ${request2.result.data.past_transactions}`)

                    wallet.updateBalance()

                    

                    console.log("Login successful")
                    console.log("[" + wallet.username + "]" + "      details:")
                    
                    console.log("         available balance :" + wallet.available)
                    console.log("         pending balance :" + wallet.pending)
                    console.log("         total balance :" + wallet.total)


                }


                };
    
        
        }

        request.onerror = (event) => {
            console.error("request (loginOffline) ERROR!!")
        }
        


// let sleepMs = 1500

// console.log("(loginOffline) Sleeping for " + sleepMs + "ms...")
// await sleep(sleepMs)
// console.log("(loginOffline) Done sleeping")
 

// console.log("ppppppppppppppp  " + walletDict + "  ppppppppppppppp" )

// console.log("ooooooooooooooo  " + walletDict + "  ooooooooooooooo" )

// console.log("popoppo   " + wallet.username + "   popoppo")





}



// if (window.locationhref == "wallet_ui.html"){
//     console.log("================================")
//     console.log("window.href = " + window.href)
//     console.log("================================")
//     loginOffline(username, password)
// }







// +

// wallet.username = "graeber"

// // // wallet.saveTransactions()


// // let testChain = [{"index": 1, "timestamp": 1730480510.3574343, "transactions": [], "proof": 100, "previous_hash": 1}, {"index": 2, "timestamp": 1730480629.2533815, "transactions": [{"sender": "f2f6155aeb5343a594ed23b26f95fae6", "recipient": "test_x", "amount": "0.0", "transaction_id": "8ae9fc367855461c992bbb2758f6f6b4"}, {"sender": "0", "recipient": "8c01184582174ce19b01aa31e26c6a1f", "amount": 1, "transaction_id": "29d8ba27ac1e492685e5597c9bea350f"}], "proof": 888273, "previous_hash": "6e90578eded256a98e8e1112132be099045371d936b37428d504bb5554c60d68"}]
// wallet.address = "8c01184582174ce19b01aa31e26c6a1f"

// // wallet.address = "861ab4092eb64d5ebbbad64302319c99"
// wallet.nodes = new Set(["127.0.0.1:5122", "127.0.0.1:5138", "127.0.0.1:5142", "127.0.0.1:5126", "127.0.0.1:5130", "127.0.0.1:5146", "127.0.0.1:5134"])

// +


//---------------------------

// wallet.readChain(testChain)

// wallet.updateBalance()

// wallet.send("test", 0)

//---------------------------

// wallet.requestTest()



// wallet.createWalletFile("mbembe")









// console.log("wallet.requestMapTest()")
// wallet.requestMapTest()
// console.log("wallet.requestMapTest()")


// registerOffline("endnotes", "password")



            


              










// loginOffline("endnotes", "password")
// console.log("__lolo_" + wallet.username + "__lolo_")
// wallet.registerNode(["127.0.0.1:5122","127.0.0.1:5138","127.0.0.1:5118","127.0.0.1:5126","127.0.0.1:5130","127.0.0.1:5146","127.0.0.1:5134"])


