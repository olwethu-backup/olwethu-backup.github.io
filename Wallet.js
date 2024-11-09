const fs = require("fs")
const axios = require("axios").default




class Wallet{

    //Javascript port of blockchain_wallet.py

    constructor(){
        this.username = ''
        this.address = "str(uuid4()).replace('-', '')"
        this.available = 0
        this.pending = 0
        this.total = this.available + this.pending
        this.nodes = new Set()
        this.port = -1
        this.pastTransactions = {}

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

    saveTransaction(transaction){
        let walletStr= ""
        let walletDict = ""
        fs.readFile(this.username + "_wallet.json", (err, inputD) => {
                
            if (err){
                throw err;
            }

            walletStr += inputD.toString()
            console.log(inputD.toString())
            walletDict = JSON.parse(walletStr)

            console.log("---------------------------")
        
            console.log(walletDict['nodes'])

            // walletDict["past_transactions"] = this.pastTransactions
            let tempPastTransactions = walletDict["past_transactions"]

            tempPastTransactions[transaction["transaction_id"]] = transaction

            walletDict["past_transactions"] = tempPastTransactions

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

    saveTransactions(){

        let walletStr= ""
        let walletDict = ""
        fs.readFile(this.username + "_wallet.json", (err, inputD) => {
                
            if (err){
                throw err;
            }

            walletStr += inputD.toString()
            console.log(inputD.toString())
            walletDict = JSON.parse(walletStr)

            console.log("---------------------------")
        
            console.log(walletDict['nodes'])

            walletDict["past_transactions"] = this.pastTransactions
            

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

                    if(transaction["transaction_id"] in this.pastTransactions){
                        if (this.pastTransactions[transactions["transaction_id"]]["status"] == "pending"){
                            this.pastTransactions[transaction["transaction_id"]] = "confirmed"
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
                    if (transaction["transaction_id"] in this.pastTransactions){
                        if (this.pastTransactions[transaction["transaction_id"]]["status"] == "pending"){
                            this.pastTransactions[transaction["transaction_id"]]["status"] = "confirmed"
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



    updateBalance(){
        console.log("this.nodes=" + this.nodes)
        console.log("this.nodes.size=" + this.nodes.size)
        console.log("this.nodes.values()=" + this.nodes.values())        
        
        let nodesIterator = this.nodes.values()

        let node = ""
        
        for (let n = 0; n < this.nodes.size; n++){

            node = nodesIterator.next().value

            console.log("node=" + node)

            try{
                
            }
            catch(err){

            }
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



    async requestMapTest(){

        let urls = []
        console.log("-1-")
        console.log("this.nodes.size=" + this.nodes.size)

        let nodesIterator = this.nodes.values()

        let node = ""



        for (let i = 0; i < this.nodes.size; i++){
            node = nodesIterator.next().value
            urls.push(axios.get("http://" + node + "/chain"))
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

wallet.username = "goldman"

// wallet.saveTransactions()


let testChain = [{"index": 1, "timestamp": 1730480510.3574343, "transactions": [], "proof": 100, "previous_hash": 1}, {"index": 2, "timestamp": 1730480629.2533815, "transactions": [{"sender": "f2f6155aeb5343a594ed23b26f95fae6", "recipient": "test_x", "amount": "0.0", "transaction_id": "8ae9fc367855461c992bbb2758f6f6b4"}, {"sender": "0", "recipient": "8c01184582174ce19b01aa31e26c6a1f", "amount": 1, "transaction_id": "29d8ba27ac1e492685e5597c9bea350f"}], "proof": 888273, "previous_hash": "6e90578eded256a98e8e1112132be099045371d936b37428d504bb5554c60d68"}]
wallet.address = "8c01184582174ce19b01aa31e26c6a1f"
wallet.nodes = new Set(["127.0.0.1:5122", "127.0.0.1:5138", "127.0.0.1:5142", "127.0.0.1:5126", "127.0.0.1:5130", "127.0.0.1:5146", "127.0.0.1:5134"])
wallet.readChain(testChain)

// wallet.updateBalance()
// wallet.requestTest()



// wallet.createWalletFile("mbembe")

console.log("wallet.requestMapTest()")
wallet.requestMapTest()
console.log("wallet.requestMapTest()")