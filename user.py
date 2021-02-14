import sqlite3


from flask_restful import Resource, reqparse
from flask_jwt import JWT, jwt_required
#import base64
import datetime
import json
from web3 import Web3
import hashlib

ganache_url = "http://e9f436c05305.ngrok.io/"
contract_address= "0x7F33ECC926d1d5b36C4b953181937e55C08aaadf"
web3=Web3(Web3.HTTPProvider(ganache_url))

class User:
    def __init__(self, username, password, name, contact, address, _id):
        self.wallet_id = _id
        self.email= username
        self.password = password
        self.name = name
        self.aadhar_no = address
        self.contact = contact



    @classmethod
    def find_by_username(cls, username):
        connection = sqlite3.connect('/Users/owaishetavkar/Desktop/api/data.db')
        cursor = connection.cursor()
        query = "SELECT * FROM users WHERE email=?"
        result = cursor.execute(query, (username,))
        row = result.fetchone()
        if row is not None:
            user = cls(*row)
        else:
            user = None
        connection.close()
        return user


    @classmethod
    def find_by_id(cls, _id):
            connection = sqlite3.connect('/Users/owaishetavkar/Desktop/api/data.db')
            cursor = connection.cursor()

            query = "SELECT * FROM users WHERE wallet_id=?"
            result = cursor.execute(query, (_id,))
            row = result.fetchone()
            if row is not None:
                user = cls(*row)
            else:
                user = None

            connection.close()
            return user


class Login(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('email',
                        type=str,
                        required=True,
                        help="This field cannot be left blank.")

    parser.add_argument('password',
                        type=str,
                        required=True,
                        help="This field cannot be left blank.")
    def post(self):

        data = Login.parser.parse_args()
        connection = sqlite3.connect('/Users/owaishetavkar/Desktop/api/data.db')
        cursor = connection.cursor()
        query = "SELECT * FROM users WHERE email=? and password=?"
        result = cursor.execute(query, (data["email"],data["password"],))
        row = result.fetchone()
        if row is not None:
            return True,200
        else:
            user = None
        connection.close()
        return False,400

class UserRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('email',
                        type=str,
                        required=True,
                        help="This field cannot be left blank.")

    parser.add_argument('password',
                        type=str,
                        required=True,
                        help="This field cannot be left blank.")

    parser.add_argument('name',
                        type=str,
                        required=True,
                        help="This field cannot be left blank.")

    parser.add_argument('contact',
                        type=int,
                        required=True,
                        help="This field cannot be left blank.")

    parser.add_argument('aadhar_no',
                        type=str,
                        required=True,
                        help="This field cannot be left blank.")

    def post(self):

        request_data = UserRegister.parser.parse_args()

        if User.find_by_username(request_data["email"]):
            return {"message": "A user with that username already exists"}, 400



        connection = sqlite3.connect('/Users/owaishetavkar/Desktop/api/data.db')
        cursor = connection.cursor()


        accounts=web3.eth.accounts
        id=0
        for i in accounts:
            query = "SELECT * FROM users WHERE wallet_id=?"
            result = cursor.execute(query, (i,))
            row = result.fetchone()
            if row == None:
                id=i
                break

        query = "INSERT INTO users VALUES (?, ?, ?, ?, ?,?)"
        cursor.execute(query, (request_data["email"], request_data["password"], request_data["name"], request_data["contact"], request_data["aadhar_no"], id))

        connection.commit()
        connection.close()

        return {"id": id}, 201




class CheckUser(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('email',
                        type=str,
                        required=True,
                        help="This field cannot be left blank.")



    def post(self):
        data= CheckUser.parser.parse_args()
        connection = sqlite3.connect('/Users/owaishetavkar/Desktop/api/data.db')
        cursor = connection.cursor()

        query = "SELECT * FROM users WHERE email=?"
        result = cursor.execute(query, (data["email"],))
        row = result.fetchone()
        if row is not None:
            return True, 200
        else:
            return False, 400



class GetProfile(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('email',
                        type=str,
                        required=True,
                        help="This field cannot be left blank.")
    #@jwt_required
    def post(self):
        data = GetProfile.parser.parse_args()
        save = User.find_by_username(data['email'])

        if save is None:
            return {"message": "email invalid"}, 404
        else:
             return {"wallet_id": save.wallet_id,
                     "name": save.name,
                     "aadhar_no": save.aadhar_no,
                     "contact": save.contact
                     }, 200


class Transactions(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('wallet_id',
                        type=str,
                        required=True,
                        help="This field cannot be left blank.")

    def post(self):
        data = Transactions.parser.parse_args()
        save = User.find_by_id(data['wallet_id'])

        if save is None:
            return {"message": "wallet id invalid"}, 404

        connection = sqlite3.connect('/Users/owaishetavkar/Desktop/api/data.db')
        cursor = connection.cursor()

        query = "SELECT * FROM transactions WHERE from_id=? OR to_id=?"
        result = cursor.execute(query, (data['wallet_id'], data['wallet_id'],)).fetchall()

        ll = []
        for i in range(len(result)):
            tp = {
                "id": result[i][0],
                "from_wallet": result[i][1],
                "amount": result[i][2],
                "to_wallet": result[i][3],
                "from_user_name": result[i][4],
                "to_user_name": result[i][5]
            }
            ll.append(tp)
        final = []
        final.append(len(ll))
        final.append(ll)


        connection.close()

        return final, 200


class GetBal(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('wallet_id',
                        type=str,
                        required=True,
                        help="This field cannot be left blank.")



    #@jwt_required
    def post(self):
        data = GetBal.parser.parse_args()



        web3.eth.default_account = data["wallet_id"]
        abi = json.loads(
            '[{"inputs":[{"internalType":"address","name":"investor","type":"address"},{"internalType":"uint256","name":"inr_invested","type":"uint256"}],"name":"buy_obsidians","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"investor","type":"address"}],"name":"equity_in_obsidian","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"inr_obsidians","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"max_obsidians","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"total_obsidian_bought","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"seller","type":"address"},{"internalType":"address","name":"buyer","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transfer_obsidian","outputs":[],"stateMutability":"nonpayable","type":"function"}]')
        contract = web3.eth.contract(
            address=contract_address,
            abi=abi
        )
        x = contract.functions.equity_in_obsidian(data["wallet_id"]).call()



        return x, 200


class NewContract(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument('employerEmail',
                        type=str,
                        required=True,
                        help="This field cannot be left blank.")

    parser.add_argument('employerWalletId',
                        type=str,
                        required=True,
                        help="This field cannot be left blank.")

    parser.add_argument('emplyeeEmail',
                        type=str,
                        required=True,
                        help="This field cannot be left blank.")

    parser.add_argument('hourRate',
                        type=float,
                        required=True,
                        help="This field cannot be left blank.")

    parser.add_argument('duration',
                        type=int,
                        required=True,
                        help="This field cannot be left blank.")

    parser.add_argument('leavesAllowed',
                        type=int,
                        required=True,
                        help="This field cannot be left blank.")

    parser.add_argument('leavesPenalty',
                        type=int,
                        required=True,
                        help="This field cannot be left blank.")

    parser.add_argument('earlyBonus',
                        type=int,
                        required=True,
                        help="This field cannot be left blank.")

    parser.add_argument('overdueCharge',
                        type=int,
                        required=True,
                        help="This field cannot be left blank.")

    def post(self):
        data = NewContract.parser.parse_args()

        if not User.find_by_username(data["emplyeeEmail"]):
            return {"message": "Employee Does not Exist"}, 400

        connection = sqlite3.connect('/Users/owaishetavkar/Desktop/api/data.db')
        cursor = connection.cursor()


        query = "SELECT * FROM users WHERE email=?"
        result = cursor.execute(query, (data["emplyeeEmail"],)).fetchone()



        query = "INSERT INTO offers VALUES (NULL, ?, ?, ?, ?, ?,?, ?, ?, ?, ?, NULL, ?)"
        cursor.execute(query, (data["employerEmail"], data["employerWalletId"], data["emplyeeEmail"], result[5] ,data["hourRate"],data["duration"],
                               data["leavesAllowed"] ,data["leavesPenalty"], data["earlyBonus"] ,0, data["overdueCharge"]))


        connection.commit()
        connection.close()
        return True, 200

class ListCanceled(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument('email',
                        type=str,
                        required=True,
                        help="This field cannot be left blank.")

    def post(self):
        data = ListCanceled.parser.parse_args()
        connection = sqlite3.connect('/Users/owaishetavkar/Desktop/api/data.db')
        cursor = connection.cursor()
        query = "SELECT * FROM offers WHERE emplyeeEmail=? and status=10"
        result = cursor.execute(query, (data["email"],)).fetchall()

        ll = []
        for i in range(len(result)):
            tp = {
                "id": result[i][0],
                "employerEmail" : result[i][1] ,
                "emplyeeEmail": result[i][3],
                "hourRate": result[i][5],
                "duration": result[i][6],
                "leavesAllowed": result[i][7],
                "leavesPenalty": result[i][8],
                "earlyBonus": result[i][9],
                "overdueCharge": result[i][12],
            }
            ll.append(tp)
        final = []
        final.append(len(ll))
        final.append(ll)
        connection.close()
        return final, 200



class ListPending(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument('email',
                        type=str,
                        required=True,
                        help="This field cannot be left blank.")

    def post(self):
        data = ListPending.parser.parse_args()
        connection = sqlite3.connect('/Users/owaishetavkar/Desktop/api/data.db')
        cursor = connection.cursor()
        query = "SELECT * FROM offers WHERE emplyeeEmail=? and status=0"
        result = cursor.execute(query, (data["email"],)).fetchall()

        ll = []
        for i in range(len(result)):
            tp = {
                "id": result[i][0],
                "employerEmail" : result[i][1] ,
                "emplyeeEmail": result[i][3],
                "hourRate": result[i][5],
                "duration": result[i][6],
                "leavesAllowed": result[i][7],
                "leavesPenalty": result[i][8],
                "earlyBonus": result[i][9],
                "overdueCharge": result[i][12],

            }
            ll.append(tp)
        final = []
        final.append(len(ll))
        final.append(ll)
        connection.close()
        return final, 200

class ListOngoing(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument('email',
                        type=str,
                        required=True,
                        help="This field cannot be left blank.")

    def post(self):
        data = ListOngoing.parser.parse_args()
        connection = sqlite3.connect('/Users/owaishetavkar/Desktop/api/data.db')
        cursor = connection.cursor()
        query = "SELECT * FROM offers WHERE emplyeeEmail=? and status=1"
        result = cursor.execute(query, (data["email"],)).fetchall()

        ll = []
        for i in range(len(result)):
            tp = {
                "id": result[i][0],
                "employerEmail": result[i][1],
                "emplyeeEmail": result[i][3],
                "hourRate": result[i][5],
                "duration": result[i][6],
                "leavesAllowed": result[i][7],
                "leavesPenalty": result[i][8],
                "earlyBonus": result[i][9],
                "contractAddress": result[i][11],
                "overdueCharge": result[i][12]

            }
            ll.append(tp)
        final = []
        final.append(len(ll))
        final.append(ll)

        connection.close()

        return final, 200

class ListCompleted(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument('email',
                        type=str,
                        required=True,
                        help="This field cannot be left blank.")

    def post(self):
        data = ListOngoing.parser.parse_args()
        connection = sqlite3.connect('/Users/owaishetavkar/Desktop/api/data.db')
        cursor = connection.cursor()
        query = "SELECT * FROM offers WHERE emplyeeEmail=? and status=2"
        result = cursor.execute(query, (data["email"],)).fetchall()

        ll = []
        for i in range(len(result)):
            tp = {
                "id": result[i][0],
                "employerEmail": result[i][1],
                "emplyeeEmail": result[i][3],
                "hourRate": result[i][5],
                "duration": result[i][6],
                "leavesAllowed": result[i][7],
                "leavesPenalty": result[i][8],
                "earlyBonus": result[i][9],
                "contractAddress": result[i][11],
                "overdueCharge": result[i][12]

            }
            ll.append(tp)
        final = []
        final.append(len(ll))
        final.append(ll)

        connection.close()

        return final, 200

class AcceptContract(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument('id',
                        type=int,
                        required=True,
                        help="This field cannot be left blank.")

    def post(self):
        data = AcceptContract.parser.parse_args()



        connection = sqlite3.connect('/Users/owaishetavkar/Desktop/api/data.db')
        cursor = connection.cursor()

        query = "SELECT * FROM offers WHERE id=?"
        result = cursor.execute(query, (data["id"],)).fetchone()





        web3.eth.default_account=result[2]
        abi = json.loads(
            '[{"inputs":[],"name":"calculate_amount","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"string","name":"Employer","type":"string"},{"internalType":"string","name":"Employee","type":"string"},{"internalType":"uint256","name":"nola","type":"uint256"},{"internalType":"uint256","name":"elp","type":"uint256"},{"internalType":"uint256","name":"hr","type":"uint256"},{"internalType":"uint256","name":"isbonus","type":"uint256"},{"internalType":"uint256","name":"duration","type":"uint256"},{"internalType":"uint256","name":"bonusamount","type":"uint256"},{"internalType":"uint256","name":"overdue","type":"uint256"}],"name":"setdata","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"setorderstatus","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"setpaymentstatus","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"leaves","type":"uint256"},{"internalType":"uint256","name":"hoursworked","type":"uint256"}],"name":"setpostcontractdata","outputs":[],"stateMutability":"payable","type":"function"}]')
        bytecode = '6080604052600080556000600155600060025560006003556000600460006101000a81548160ff0219169083151502179055506000600460016101000a81548160ff0219169083151502179055506000600460026101000a81548160ff0219169083151502179055506040518060400160405280600481526020017f6e6f6e6500000000000000000000000000000000000000000000000000000000815250600590805190602001906100b392919061012b565b506040518060400160405280600481526020017f6e6f6e6500000000000000000000000000000000000000000000000000000000815250600690805190602001906100ff92919061012b565b506000600755600060085560006009556000600a556000600b5534801561012557600080fd5b506101d6565b828054600181600116156101000203166002900490600052602060002090601f01602090048101928261016157600085556101a8565b82601f1061017a57805160ff19168380011785556101a8565b828001600101855582156101a8579182015b828111156101a757825182559160200191906001019061018c565b5b5090506101b591906101b9565b5090565b5b808211156101d25760008160009055506001016101ba565b5090565b6104dc806101e56000396000f3fe60806040526004361061004a5760003560e01c806303bf0a861461004f57806318db29c8146100875780633c4371f6146100b25780639aa94464146100d2578063df72035a146100f2575b600080fd5b6100856004803603604081101561006557600080fd5b81019080803590602001909291908035906020019092919050505061028b565b005b34801561009357600080fd5b5061009c6102b8565b6040518082815260200191505060405180910390f35b6100ba61032e565b60405180821515815260200191505060405180910390f35b6100da610352565b60405180821515815260200191505060405180910390f35b610289600480360361012081101561010957600080fd5b810190808035906020019064010000000081111561012657600080fd5b82018360208201111561013857600080fd5b8035906020019184600183028401116401000000008311171561015a57600080fd5b91908080601f016020809104026020016040519081016040528093929190818152602001838380828437600081840152601f19601f820116905080830192505050505050509192919290803590602001906401000000008111156101bd57600080fd5b8201836020820111156101cf57600080fd5b803590602001918460018302840111640100000000831117156101f157600080fd5b91908080601f016020809104026020016040519081016040528093929190818152602001838380828437600081840152601f19601f82011690508083019250505050505050919291929080359060200190929190803590602001909291908035906020019092919080359060200190929190803590602001909291908035906020019092919080359060200190929190505050610376565b005b80600981905550816008819055506000600460026101000a81548160ff0219169083151502179055505050565b6000806000905060015460095411156102dc57600154600054029050600b54810390505b60015460095410156102f2576009546000540290505b6002546008541115610314576000600254600854039050600354810282039150505b6001600754141561032757600a54810190505b8091505090565b60006001600460006101000a81548160ff0219169083151502179055506001905090565b60006001600460016101000a81548160ff0219169083151502179055506001905090565b886005908051906020019061038c9291906103fb565b5087600690805190602001906103a39291906103fb565b506001600460026101000a81548160ff021916908315150217905550866002819055508560038190555084600081905550836007819055508260018190555081600a8190555080600b81905550505050505050505050565b828054600181600116156101000203166002900490600052602060002090601f0160209004810192826104315760008555610478565b82601f1061044a57805160ff1916838001178555610478565b82800160010185558215610478579182015b8281111561047757825182559160200191906001019061045c565b5b5090506104859190610489565b5090565b5b808211156104a257600081600090555060010161048a565b509056fea2646970667358221220e187c85f5228ef2028edbe0c6fdd1280d389feaf610a7c81f2af286ef6da787164736f6c63430007040033'

        Deal = web3.eth.contract(abi=abi, bytecode=bytecode)

        tx_hash = Deal.constructor().transact()


        tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)

        isbonus=0

        if result[9]!=0:
            isbonus=1


        contract1 = web3.eth.contract(
           address=tx_receipt.contractAddress,
            abi=abi
        )


        x=contract1.functions.setdata(result[1], result[3], result[7], result[8], int(result[5]),isbonus, result[6], result[9], result[12]).transact()

        query = "UPDATE offers SET contractAddress=? WHERE id=?"
        lol = (tx_receipt.contractAddress ,data['id'],)
        cursor.execute(query, lol)
        query = "UPDATE offers SET status=1 WHERE id=?"
        lol = (data['id'],)
        cursor.execute(query, lol)
        connection.commit()
        connection.close()

        return tx_receipt.contractAddress, 201


class Cancel(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument('id',
                        type=int,
                        required=True,
                        help="This field cannot be left blank.")

    def post(self):
        data = Cancel.parser.parse_args()
        connection = sqlite3.connect('/Users/owaishetavkar/Desktop/api/data.db')
        cursor = connection.cursor()
        query = "UPDATE offers SET status=10 WHERE id=?"
        lol = (data['id'],)
        cursor.execute(query, lol)

        connection.commit()
        connection.close()


class Completed(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument('id',
                        type=int,
                        required=True,
                        help="This field cannot be left blank.")

    parser.add_argument('leaves',
                        type=int,
                        required=True,
                        help="This field cannot be left blank.")

    parser.add_argument('hoursWorked',
                        type=int,
                        required=True,
                        help="This field cannot be left blank.")





    def post(self):
        data = Completed.parser.parse_args()

        connection = sqlite3.connect('/Users/owaishetavkar/Desktop/api/data.db')
        cursor = connection.cursor()
        
        query = "SELECT * FROM offers WHERE id=?"
        result = cursor.execute(query, (data["id"],)).fetchone()

        
        

        web3.eth.default_account=result[2]
        abi = json.loads(
            '[{"inputs":[],"name":"calculate_amount","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"string","name":"Employer","type":"string"},{"internalType":"string","name":"Employee","type":"string"},{"internalType":"uint256","name":"nola","type":"uint256"},{"internalType":"uint256","name":"elp","type":"uint256"},{"internalType":"uint256","name":"hr","type":"uint256"},{"internalType":"uint256","name":"isbonus","type":"uint256"},{"internalType":"uint256","name":"duration","type":"uint256"},{"internalType":"uint256","name":"bonusamount","type":"uint256"},{"internalType":"uint256","name":"overdue","type":"uint256"}],"name":"setdata","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"setorderstatus","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"setpaymentstatus","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"leaves","type":"uint256"},{"internalType":"uint256","name":"hoursworked","type":"uint256"}],"name":"setpostcontractdata","outputs":[],"stateMutability":"payable","type":"function"}]')
        bytecode = '6080604052600080556000600155600060025560006003556000600460006101000a81548160ff0219169083151502179055506000600460016101000a81548160ff0219169083151502179055506000600460026101000a81548160ff0219169083151502179055506040518060400160405280600481526020017f6e6f6e6500000000000000000000000000000000000000000000000000000000815250600590805190602001906100b392919061012b565b506040518060400160405280600481526020017f6e6f6e6500000000000000000000000000000000000000000000000000000000815250600690805190602001906100ff92919061012b565b506000600755600060085560006009556000600a556000600b5534801561012557600080fd5b506101d6565b828054600181600116156101000203166002900490600052602060002090601f01602090048101928261016157600085556101a8565b82601f1061017a57805160ff19168380011785556101a8565b828001600101855582156101a8579182015b828111156101a757825182559160200191906001019061018c565b5b5090506101b591906101b9565b5090565b5b808211156101d25760008160009055506001016101ba565b5090565b6104dc806101e56000396000f3fe60806040526004361061004a5760003560e01c806303bf0a861461004f57806318db29c8146100875780633c4371f6146100b25780639aa94464146100d2578063df72035a146100f2575b600080fd5b6100856004803603604081101561006557600080fd5b81019080803590602001909291908035906020019092919050505061028b565b005b34801561009357600080fd5b5061009c6102b8565b6040518082815260200191505060405180910390f35b6100ba61032e565b60405180821515815260200191505060405180910390f35b6100da610352565b60405180821515815260200191505060405180910390f35b610289600480360361012081101561010957600080fd5b810190808035906020019064010000000081111561012657600080fd5b82018360208201111561013857600080fd5b8035906020019184600183028401116401000000008311171561015a57600080fd5b91908080601f016020809104026020016040519081016040528093929190818152602001838380828437600081840152601f19601f820116905080830192505050505050509192919290803590602001906401000000008111156101bd57600080fd5b8201836020820111156101cf57600080fd5b803590602001918460018302840111640100000000831117156101f157600080fd5b91908080601f016020809104026020016040519081016040528093929190818152602001838380828437600081840152601f19601f82011690508083019250505050505050919291929080359060200190929190803590602001909291908035906020019092919080359060200190929190803590602001909291908035906020019092919080359060200190929190505050610376565b005b80600981905550816008819055506000600460026101000a81548160ff0219169083151502179055505050565b6000806000905060015460095411156102dc57600154600054029050600b54810390505b60015460095410156102f2576009546000540290505b6002546008541115610314576000600254600854039050600354810282039150505b6001600754141561032757600a54810190505b8091505090565b60006001600460006101000a81548160ff0219169083151502179055506001905090565b60006001600460016101000a81548160ff0219169083151502179055506001905090565b886005908051906020019061038c9291906103fb565b5087600690805190602001906103a39291906103fb565b506001600460026101000a81548160ff021916908315150217905550866002819055508560038190555084600081905550836007819055508260018190555081600a8190555080600b81905550505050505050505050565b828054600181600116156101000203166002900490600052602060002090601f0160209004810192826104315760008555610478565b82601f1061044a57805160ff1916838001178555610478565b82800160010185558215610478579182015b8281111561047757825182559160200191906001019061045c565b5b5090506104859190610489565b5090565b5b808211156104a257600081600090555060010161048a565b509056fea2646970667358221220e187c85f5228ef2028edbe0c6fdd1280d389feaf610a7c81f2af286ef6da787164736f6c63430007040033'

        contract1 = web3.eth.contract(
            address=result[11],
            abi=abi
        )
        contract1.functions.setpostcontractdata(data["leaves"], data["hoursWorked"])
        ans=contract1.functions.calculate_amount().call()

        query = "UPDATE offers SET status=2 WHERE id=?"
        lol = (data['id'],)
        cursor.execute(query, lol)
        connection.commit()
        connection.close()

        web3.eth.default_account = result[2]
        abi = json.loads(
            '[{"inputs":[{"internalType":"address","name":"investor","type":"address"},{"internalType":"uint256","name":"inr_invested","type":"uint256"}],"name":"buy_obsidians","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"investor","type":"address"}],"name":"equity_in_obsidian","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"inr_obsidians","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"max_obsidians","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"total_obsidian_bought","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"seller","type":"address"},{"internalType":"address","name":"buyer","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transfer_obsidian","outputs":[],"stateMutability":"nonpayable","type":"function"}]')
        contract = web3.eth.contract(
            address=contract_address,
            abi=abi
        )


        contract.functions.transfer_obsidian(result[2], result[4], ans*2).transact()


        connection = sqlite3.connect('/Users/owaishetavkar/Desktop/api/data.db')
        cursor = connection.cursor()


        query = "INSERT INTO transactions VALUES (NULL, ?, ?, ?, ?, ?)"
        cursor.execute(query, (result[2], ans*2, result[4], result[1] , result[3]))

        connection.commit()
        connection.close()


        return {"final payout": ans*2}, 200

class EmpContracts(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument('email',
                        type=str,
                        required=True,
                        help="This field cannot be left blank.")

    def post(self):
        data= EmpContracts.parser.parse_args()
        connection = sqlite3.connect('/Users/owaishetavkar/Desktop/api/data.db')
        cursor = connection.cursor()
        query = "SELECT * FROM offers WHERE employerEmail=?"
        result = cursor.execute(query, (data["email"],)).fetchall()

        ll = []
        for i in range(len(result)):
            if result[i][10]==0:
                status="Pending"
            elif result[i][10]==1:
                status="In Process"
            elif result[i][10]==2:
                status="Completed"
            else:
                status="Rejected"
            tp = {
                "id": result[i][0],
                "employerEmail": result[i][1],
                "emplyeeEmail": result[i][3],
                "hourRate": result[i][5],
                "duration": result[i][6],
                "leavesAllowed": result[i][7],
                "leavesPenalty": result[i][8],
                "earlyBonus": result[i][9],
                "status": status,
                "contractAddress": result[i][11],
                "overdueCharge": result[i][12]
            }
            ll.append(tp)
        final = []
        final.append(len(ll))
        final.append(ll)

        connection.close()

        return final,200


class Buy(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument('wallet_id',
                        type=str,
                        required=True,
                        help="This field cannot be left blank.")
                        
    parser.add_argument('amount',
                        type=str,
                        required=True,
                        help="This field cannot be left blank.")
    
    def post(self):
        data = Buy.parser.parse_args()
    
        
        web3.eth.default_account=data['wallet_id']


        abi=json.loads('[{"inputs":[{"internalType":"address","name":"investor","type":"address"},{"internalType":"uint256","name":"inr_invested","type":"uint256"}],"name":"buy_obsidians","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"investor","type":"address"}],"name":"equity_in_obsidian","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"inr_obsidians","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"max_obsidians","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"total_obsidian_bought","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"seller","type":"address"},{"internalType":"address","name":"buyer","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transfer_obsidian","outputs":[],"stateMutability":"nonpayable","type":"function"}]')
        contract=web3.eth.contract(
        address=contract_address,
        abi=abi
        )
        x=contract.functions.buy_obsidians(data['wallet_id'],int(data['amount'])).transact()
        y=contract.functions.equity_in_obsidian(data['wallet_id']).call()

        connection = sqlite3.connect('/Users/owaishetavkar/Desktop/api/data.db')
        cursor = connection.cursor()

        query = "INSERT INTO transactions VALUES (NULL, ?, ?, ?, ?, ? )"
        cursor.execute(query, ("Deposit", int(data["amount"]), data["wallet_id"], "Self Crypto Purchase", "Self Transfer"))

        connection.commit()
        connection.close()

        return {"new balance":y},200




class Transfer(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument('wallet_id',
                        type=str,
                        required=True,
                        help="This field cannot be left blank.")

    parser.add_argument('transfereeEmail',
                        type=str,
                        required=True,
                        help="This field cannot be left blank.")
    
    parser.add_argument('amount',
                        type=int,
                        required=True,
                        help="This field cannot be left blank.")

    def post(self):
        data = Transfer.parser.parse_args()
        
        connection = sqlite3.connect('/Users/owaishetavkar/Desktop/api/data.db')
        cursor = connection.cursor()


        query = "SELECT * FROM users WHERE email=?"
        result = cursor.execute(query, (data["transfereeEmail"],)).fetchone()

        web3.eth.default_account=data['wallet_id']
        abi=json.loads('[{"inputs":[{"internalType":"address","name":"investor","type":"address"},{"internalType":"uint256","name":"inr_invested","type":"uint256"}],"name":"buy_obsidians","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"investor","type":"address"}],"name":"equity_in_obsidian","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"inr_obsidians","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"max_obsidians","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"total_obsidian_bought","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"seller","type":"address"},{"internalType":"address","name":"buyer","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transfer_obsidian","outputs":[],"stateMutability":"nonpayable","type":"function"}]')
        contract=web3.eth.contract(
        address=contract_address,
        abi=abi
        )
        query = "SELECT * FROM users WHERE wallet_id=?"
        result1 = cursor.execute(query, (data["wallet_id"],)).fetchone()



        query = "INSERT INTO transactions VALUES (NULL, ?, ?, ?, ?, ? )"
        cursor.execute(query, (data["wallet_id"], data["amount"], result[5], result1[0] , data['transfereeEmail']))

        connection.commit()
        connection.close()



        if(contract.functions.equity_in_obsidian(data['wallet_id']).call()>=data["amount"]):
            contract.functions.transfer_obsidian(data["wallet_id"],result[5],data['amount']).transact()
            y = contract.functions.equity_in_obsidian(data['wallet_id']).call()
            return {"new balance": y}, 200
        else:
            return {"message": "Not enough funds in Account"}, 400


