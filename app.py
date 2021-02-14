from flask import Flask, request
from flask_restful import Resource, Api
from flask_jwt import JWT, jwt_required

from security import authenticate, identity
from user import GetProfile, UserRegister, CheckUser, GetBal, Transactions, Login, NewContract, ListPending, ListOngoing, ListCompleted, Buy, Transfer, EmpContracts, Completed, ListCanceled, Cancel
from user import AcceptContract


import json


from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'safety'
api = Api(app)

# app.config['JWT_AUTH_URL_RULE'] = '/login'
app.config['JWT_EXPIRATION_DELTA'] = timedelta(seconds=99999999999)
api.add_resource(Login, '/login')


jwt = JWT(app, authenticate, identity)  # authentication

api.add_resource(UserRegister, '/sign_up')


api.add_resource(CheckUser, '/check_user')
api.add_resource(GetProfile, '/get_profile')

api.add_resource(GetBal, '/get_bal')
api.add_resource(Transactions, '/transactions')


api.add_resource(NewContract, '/new_contract')

api.add_resource(ListPending, '/list_pending')
api.add_resource(ListOngoing, '/list_ongoing')
api.add_resource(ListCompleted, '/list_completed')
api.add_resource(ListCanceled, '/list_canceled')



api.add_resource(EmpContracts, '/emp_contracts')

api.add_resource(AcceptContract, '/accept_contract')
api.add_resource(Completed, '/complete')
api.add_resource(Cancel, '/decline_contract')

api.add_resource(Transfer, '/transfer')

api.add_resource(Buy, '/buy')









if __name__ == "__main__":
    app.run(port=5000, debug=True)
