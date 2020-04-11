import re

import datetime
import graphene as graphene
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.models import User
import uuid

from extuser.models import RestorePswdByEmail

restorePasswordMailTitle = 'restorePasswordMailTitle'
restorePasswordFromEmail = ''

phone_regexp = r'\+?7\s*(\d{3})\s*(\d{3})-?(\d{2})-?(\d{2})'

class Logout(graphene.Mutation):
    ok = graphene.Boolean()
    @classmethod
    def mutate(cls, root, info, **args):
        logout(info.context)
        return cls(ok=True)



class updateProfile(graphene.Mutation):
    ok = graphene.Boolean()

    class Arguments:
        lastname = graphene.String(required=True)
        firstname = graphene.String(required=True)
        phone = graphene.String(required=True)
        email = graphene.String(required=False)

    @classmethod
    def mutate(cls, root, info, **args):
        user = info.context.user
        if not user or user.is_anonymous:
            return cls(ok=False)

        lastname = args.get('lastname')
        if lastname:
            lastname = lastname.strip()

        firstname = args.get('firstname')
        if firstname:
            firstname = firstname.strip()

        phone = args.get('phone')
        if phone:
            phone = phone.strip()

        email = args.get('email')
        if email:
            email = email.strip()
        email = args.get('email')
        if email:
            email=email.strip()

        m = re.match(r'[^@]+@[^@]+\.[^@]+', email)
        if not m:
            return cls(ok=False)

        m = re.match(phone_regexp, phone)
        if m:
            phone = '7' + m.group(1) + m.group(2) + m.group(3) + m.group(4)
        else:
            return cls(ok=False)

        user.username = phone
        user.first_name = firstname
        user.last_name = lastname
        user.email = email
        user.save()

        return cls(
            ok=True,
        )


class restorePassword(graphene.Mutation):
    ok = graphene.Boolean()

    restoreMsgTemplate = u'Мы получили запрос на восстановление доступа к вашей учётной записи на сайте ********, которая привязана к почте {}. \n\n' \
        u'Если это были вы, перейдите по ссылке, которая будет активна до {}:\n\n' \
        u' http://*********/confirm/{}\n\n ' \
        u'Скопируйте ссылку и откройте через адресную строку браузера, если она не работает.\n\n' \
        u'Если вы не запрашивали изменение пароля, проигнорируйте это письмо.'

    class Arguments:
        login = graphene.String(required=True)

    @classmethod
    def mutate(cls, root, info, **args):
        user = info.context.user
        if user and not user.is_anonymous:
            return cls(ok=False)

        login = args.get('login')
        if login:
            login = login.strip()

        m = re.match(phone_regexp, login)
        if m:
            phone = '7' + m.group(1) + m.group(2) + m.group(3) + m.group(4)
        else:
            return cls(ok=False)

        user = User.objects.get(username=phone)

        reg = RestorePswdByEmail()
        reg.session_key = info.context.session.session_key
        reg.login = phone
        reg.code = str(uuid.uuid4())
        reg.save()
        txt = cls.restoreMsgTemplate.format(user.email, '...', reg.code)
        #send_mail(u'Восстановление пароля domsad-mgn.ru', txt, 'nash34@gmail.com', [user.email], fail_silently=False)
        send_mail(restorePasswordMailTitle, txt, restorePasswordFromEmail, [user.email], fail_silently=False)
        return cls(
            ok=True,
        )

class confirmRestorePassword(graphene.Mutation):
    ok = graphene.Boolean()

    class Arguments:
        code = graphene.String(required=True)

    @classmethod
    def mutate(cls, root, info, **args):
        user = info.context.user
        if user and not user.is_anonymous:
            logout(info.context)

        code = args.get('code')
        if code:
            code = code.strip()
        try:
            reg = RestorePswdByEmail.objects.get(
                code=code,
                creation__gte=datetime.datetime.now()-datetime.timedelta(seconds=60*60*24*3),
                checked=False,
            )
            #reg.checked = True
            #reg.save()
        except RestorePswdByEmail.DoesNotExist:
            return cls(ok=False)


        return cls(
            ok=True,
        )


class changePassword(graphene.Mutation):
    ok = graphene.Boolean()

    class Arguments:
        code = graphene.String(required=True)
        password = graphene.String(required=True)

    @classmethod
    def mutate(cls, root, info, **args):
        mode = 0
        user = info.context.user
        code = args.get('code')
        if code:
            code = code.strip()
        if user and not user.is_anonymous:
            if not user.check_password(code):
                return cls(ok=False)
            else:
                mode = 1

        password = args.get('password')
        if password:
            password = password.strip()

        if mode==1:
            user.set_password(password)
            user.save()
            update_session_auth_hash(info.context, user)
        else:
            try:
                reg = RestorePswdByEmail.objects.get(
                    code=code,
                    creation__gte=datetime.datetime.now()-datetime.timedelta(seconds=60*60*24*3),
                    checked=False,
                )
                u = User.objects.get(username=reg.login)
                u.set_password(password)
                u.save()
                reg.checked = True
                reg.save()
            except RestorePswdByEmail.DoesNotExist:
                return cls(ok=False)

        return cls(
            ok=True,
        )

class Mutation():
    updateProfile = updateProfile.Field()
    restorePassword = restorePassword.Field()
    confirmRestorePassword = confirmRestorePassword.Field()
    changePassword = changePassword.Field()
    logout = Logout.Field()
