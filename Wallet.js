const fs = require("fs")
const axios = require("axios").default

const uuid =  require('uuid')


function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}



class Wallet{

    //Javascript port of blockchain_wallet.py

    constructor(){
        this.username = ''
        this.address = uuid.v4().replaceAll("-", "")
        this.available = 0
        this.pending = 0
        this.total = this.available + this.pending
        this.nodes = new Set()
        this.port = -1
        this.pastTransactions = new Map()

    }

    createWalletFile(username){

        let walletDict = "{}"
        fs.writeFile(username + "_wallet.json", walletDict, (err) => {
                    if (err) {
                        throw err;
                    }
                    else{
                        console.log("updated " + username + "_wallet.json")
                    }
        })
    }

    saveTransaction(transactionMap){
        let transaction =  Object.fromEntries(transactionMap)
        console.log("transaction = "+ + transaction)

        let walletStr= ""
        let walletDict = ""
        fs.readFile(this.username + "_wallet.json", (err, inputD) => {
                
            if (err){
                throw err;
            }

            // console.log("this.username (saveTransaction) = " + this.username)
            // console.log("inputD = " + inputD)

            walletStr += inputD.toString()

            // console.log("walletStr (saveTransaction 1) = " + walletStr)
            // console.log(inputD.toString())
            walletDict = JSON.parse(walletStr)

            // console.log("---------------------------")
            // console.log("transaction = " + transaction)
        
            // console.log(walletDict['nodes'])

            // walletDict["past_transactions"] = this.pastTransactions
            let tempPastTransactions = walletDict["past_transactions"]

            // console.log("tempPastTransactions = " + tempPastTransactions)

            tempPastTransactions[transaction["transaction_id"]] = transaction
            
            // console.log("tempPastTransactions = " + tempPastTransactions)
            
            // console.log('walletDict["past_transactions"] = ' + walletDict["past_transactions"])
            // console.log("this.pastTransactions = " + this.pastTransactions)

            walletDict["past_transactions"] = tempPastTransactions

            // console.log(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>-----------")
            // console.log('walletDict["past_transactions"] = ' + walletDict["past_transactions"])
            // console.log("this.pastTransactions = " + this.pastTransactions)
            
            // console.log("walletDict['past_transactions'] = " + walletDict["past_transactions"])
            // console.log('tempPastTransactions[transaction["transaction_id"]] = ' + tempPastTransactions[transaction["transaction_id"]])
            
            // console.log("walletDict['past_transactions'][transaction['transaction_id']] = " + walletDict['past_transactions'][transaction['transaction_id']])

            walletStr = JSON.stringify(walletDict)

            // console.log("\n?\n?\n?\n?\n?\n?\n?\n?\n?\n?\n?\n?")
            // console.log("walletStr (saveTransaction 2) = " + walletStr)
            // console.log("\n?\n?\n?\n?\n?\n?\n?\n?\n?\n?\n?\n?")

            // console.log("\n?\n?\n?\n?\n?\n?\n?\n?\n?\n?\n?\n?")
            // console.log("walletStr (saveTransaction 3) = " + walletStr)
            // console.log("\n?\n?\n?\n?\n?\n?\n?\n?\n?\n?\n?\n?")
           
            
            fs.writeFile(this.username + "_wallet.json", walletStr, (err) => {
                if (err){
                    throw err;
                }
                else{
                    console.log("updated " + this.username + "_wallet.json")
                }
            })

            console.log("done")
        })
    }
    updateFile(field, data){
        
        
        // let myUUID = uuid.v4().replaceAll("-", "")
        // console.log("UUID = " + myUUID)



        let walletStr= ""
        let walletDict = ""

        fs.readFile(this.username + "_wallet.json", (err, inputD) => {
            console.log("###############" + field + "###############")
            console.log("this.username (updateFile) = " + this.username)
            // console.log('err = ' + err)

            

            if (err){
                throw err;
            }



            console.log("inputD (updateFile) " + field + " = " + inputD)
            walletStr += inputD.toString()
            console.log("inputD.toString() (updateFile) " + field + " = " + inputD.toString())

            console.log("walletStr (updateFile) " + field + " = " + walletStr)

            walletDict = JSON.parse(walletStr)

            console.log("---------------------------")
        
            console.log(walletDict['nodes'])

            walletDict[field] = data
            

            walletStr = JSON.stringify(walletDict)

            console.log("\n!\n!\n!\n!\n!\n!\n!\n!\n!\n!\n!\n!")
            console.log("walletStr = " + walletStr)
            console.log("\n!\n!\n!\n!\n!\n!\n!\n!\n!\n!\n!\n!")
           
            
            fs.writeFile(this.username + "_wallet.json", walletStr, (err) => {
                if (err){
                    throw err;
                }
                else{
                    console.log("updated '" + field + "' of " + this.username + "_wallet.json")
                }
            })

            console.log("done")
        })
      
    }


    saveTransactions(){

        let walletStr= ""
        let walletDict = ""
        fs.readFile(this.username + "_wallet.json", (err, inputD) => {
                
            if (err){
                throw err;
            }

            walletStr += inputD.toString()
            // console.log("inputD.toString()= ")
            // console.log(inputD.toString())
            walletDict = JSON.parse(walletStr)
            // console.log("\n)\n)\n)\n)\n)\n)\n)\n)\n)\n)\n)\n)\n)\n)")
            // console.log("---------------------------")
            
            // console.log(walletDict['nodes'])
            // console.log('walletDict["past_transactions"] = ' + walletDict["past_transactions"])
            // console.log("this.pastTransactions = " + this.pastTransactions)
            walletDict["past_transactions"] = this.pastTransactions

            // console.log("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
            // console.log('walletDict["past_transactions"] = ' + walletDict["past_transactions"])
            // console.log("this.pastTransactions = " + this.pastTransactions)
            // console.log("\n)\n)\n)\n)\n)\n)\n)\n)\n)\n)\n)\n)\n)\n)")

            walletStr = JSON.stringify(walletDict)
           
            
            fs.writeFile(this.username + "_wallet.json", walletStr, (err) => {
                if (err){
                    throw err;
                }
                else{
                    console.log("updated " + this.username + "_wallet.json")
                }
            })

            console.log("done")
        })
      
    }

    async send(address, amount){


        // console.log("[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[")
        this.updateBalance()
        // console.log("[](send)\n[](send)\n[](send)\n[](send)\n[](send)\n[](send)\n[](send)\n[](send)\n[](send)\n[](send)\n[](send)\n[](send)\n")

        // console.log("this.available=" + this.available)
        
        
        


        let valuesObject = {
            "recipient": address,
            "amount": amount
        }

        valuesObject["transaction_id"] = uuid.v4().replaceAll("-", "")
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

        this.saveTransaction(valuesDict)

        console.log("this.nodes=" + this.nodes)

        let nodeResponses = await this.asyncRequest("/propagate", valuesObject)

        console.log("**********************************************************")
        console.log('nodeResponses=' + nodeResponses)
        console.log("**********************************************************")


        // console.log("[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[")








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
                        if (this.pastTransactions.get(transactions["transaction_id"])["status"] == "pending"){
                            this.pastTransactions.get(transaction["transaction_id"]) = "confirmed"
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
                            this.pastTransactions.get(transaction["transaction_id"])["status"] = "confirmed"
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
            saveTransactions()
        }
        




        


    }



    async updateBalance(){
        console.log("this.nodes=" + this.nodes)
        console.log("this.nodes.size=" + this.nodes.size)
        console.log("this.nodes.values()=" + this.nodes.values())        
        
        


        

        let urls = []

        let nodesIterator = this.nodes.values()

        let node = ""
        
        for (let n = 0; n < this.nodes.size; n++){

            node = nodesIterator.next().value

            // console.log("node=" + node)

            urls.push(axios.get("http://" + node + "/chain"))

            
        }

       let theResponses = await axios.all(urls).then(axios.spread((...responses) =>{

            // console.log('responses.length=' + responses.length)
            // for (let r = 0; r < responses.length; r++){
            //     console.log('**************')
            //     console.log(responses[r])
            //     console.log('%%%%%%%%%%%%%%')
            //     console.log("\n\n\n")
          
            // }


            
            return responses


       })).catch(errors => {
        console.error(errors)
       })

    //    console.log("theResponses=" + theResponses)
    //    for (let q = 0; q < theResponses.length; q++){
    //     console.log("]" + q + "[")
    //     console.log(theResponses[q])

    //    }

       let response = theResponses[0] //TODO: modify this to seek the longest chain that was provided

       console.log("status=" + response["status"])
       console.log("status type: " + typeof(response["status"]))

       let sleepMs = 10000

       console.log("(updateBalance) Sleeping for " + sleepMs + "ms...")
       await sleep(sleepMs)
       console.log("(updateBalance) Done sleeping")


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

        

        for (let i = 0; i < this.nodes.size; i++){

           
            node = nodesIterator.next().value
            console.log("NODE = " + node)
            console.log("))))))))))))))))))))))))))))))))))))))))))))))")
            urls.push(axios.get("http://" + node + endpoint, {params: parameters}))
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


        for (let i = 0; i < this.nodes.size; i++){
            node = nodesIterator.next().value
            urls.push(axios.get("http://" + node + "/propagate", {params: {
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

wallet = new Wallet()

wallet.username = "graeber"

// wallet.saveTransactions()


let testChain = [{"index": 1, "timestamp": 1730480510.3574343, "transactions": [], "proof": 100, "previous_hash": 1}, {"index": 2, "timestamp": 1730480629.2533815, "transactions": [{"sender": "f2f6155aeb5343a594ed23b26f95fae6", "recipient": "test_x", "amount": "0.0", "transaction_id": "8ae9fc367855461c992bbb2758f6f6b4"}, {"sender": "0", "recipient": "8c01184582174ce19b01aa31e26c6a1f", "amount": 1, "transaction_id": "29d8ba27ac1e492685e5597c9bea350f"}], "proof": 888273, "previous_hash": "6e90578eded256a98e8e1112132be099045371d936b37428d504bb5554c60d68"}]
// wallet.address = "8c01184582174ce19b01aa31e26c6a1f"

wallet.address = "861ab4092eb64d5ebbbad64302319c99"
wallet.nodes = new Set(["127.0.0.1:5122", "127.0.0.1:5138", "127.0.0.1:5142", "127.0.0.1:5126", "127.0.0.1:5130", "127.0.0.1:5146", "127.0.0.1:5134"])

//---------------------------

wallet.readChain(testChain)

wallet.updateBalance()

wallet.send("test", 0)

//---------------------------

// wallet.requestTest()



// wallet.createWalletFile("mbembe")









// console.log("wallet.requestMapTest()")
// wallet.requestMapTest()
// console.log("wallet.requestMapTest()")