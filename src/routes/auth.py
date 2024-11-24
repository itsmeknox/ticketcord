from flask import Blueprint, request, jsonify, render_template
from pydantic import BaseModel
from utils.enums import UserRole
from modules.auth import JWT

import os

jwt = JWT(os.getenv('JWT_SECRET_KEY'))


class SignupRequest(BaseModel):
    email: str
    username: str
    id: str
    role: UserRole = UserRole.CUSTOMER
    
    

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/v1/auth/signup', methods=['POST'])
def auth():
    data = SignupRequest.model_validate(request.json)
    
    token = jwt.encrypt(
        data.model_dump()
    )

    return jsonify({"token": token})
    
    

@auth_bp.route('/auth', methods=['GET'])
def auth_page():
    return render_template('auth.html')

    
    
@auth_bp.route('/support', methods=['GET'])
def support_page():
    return render_template('support.html')

@auth_bp.route('/tickets/<id>', methods=['GET'])
def chat_page(id: str):
    print(id)
    return render_template('chat.html', id=id)