import re

import graphene as graphene

phone_regexp = r'\+?7\s*(\d{3})\s*(\d{3})-?(\d{2})-?(\d{2})'


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

class Mutation():
    updateProfile = updateProfile.Field()
