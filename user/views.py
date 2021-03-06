import json
import jwt
import bcrypt

from django.views        import View
from django.http         import JsonResponse
from .models             import User
from my_settings         import SECRET_KEY, ALGORITHM


class SignUpView(View):
    def post(self, request):
        data     = json.loads(request.body)
        password = data.get('password')
        password_len = 4

        if ('email' not in data.keys() or
            'password' not in data.keys() or
            'userid' not in data.keys() or
            'address' not in data.keys() or
            'user_name' not in data.keys() or
            'phonenumber' not in data.keys() or
            'telephone' not in data.keys()):
            return JsonResponse({'message':'KEY_ERROR'},status=400)

        if not '@' in data['email'] or not '.' in data['email']:#이메일 형식이 안 맞을 때
            return JsonResponse({'message':'EMAIL_FORM_ERROR'}, status=400)

        if len(str(password)) < password_len:#비밀번호가 4자리 이하일 때
            return JsonResponse({'message':'PASSWORD_FORM_ERROR'}, status=400)

        if (User.objects.filter(userid = data['userid']) or 
            User.objects.filter(phonenumber = data['phonenumber']) or
            User.objects.filter(email = data['email'])):
            return JsonResponse({'message':'ALREADY_IN_USE'}, status=400)
    

        password = bcrypt.hashpw(
            data['password'].encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

        User(
            user_name   = data['user_name'],
            email       = data['email'],
            password    = password,
            userid      = data['userid'],
            phonenumber = data['phonenumber'],
            address     = data['address'],
            telephone   = data['telephone']
          
        ).save()

        return JsonResponse({'message':'SUCCESS'}, status=200)#그게 아니면 success 반환

    def get(self, request):
        user_data = User.objects.values()
        return JsonResponse({'users':list(user_data)}, status=200)

class LoginView(View):
    def post(self, request):
        data = json.loads(request.body)
        password = data.get('password')
        #아이디 혹은 비밀번호를 빈칸으로 두고 로그인 하려고 했을 때,
        if (data['userid'] == "" or
            data['password'] == ""):
            return JsonResponse({'message':'VALUES_ERROR'},status=400)

        if User.objects.filter(userid=data['userid']):#입력한 아이디를 조회 후
            login_user = User.objects.get(userid=data['userid'])#변수에 저장
            
            if bcrypt.checkpw(password.encode('utf-8'), login_user.password.encode('utf-8')):
                
                token = jwt.encode(
                    {
                        'userid' : login_user.id,
                    }, SECRET_KEY, algorithm = ALGORITHM).decode('utf-8')
                
                return JsonResponse({'Authorization': token}, status=200)
            
            return JsonResponse({'message':'INVALID_USER'}, status=400)



