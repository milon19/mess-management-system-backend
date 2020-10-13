from django.core.mail import EmailMessage
from django.shortcuts import render
from django.template.loader import render_to_string

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import UserProfile
from .serializers import UserProfileSerializer
from .permissions import UpdateOwnProfile
from .random_token_generate import TokenGenerator
# from django.conf import settings


def mail_send(email_to, subject, message, from_email):
    # Try to send the message.
    try:
        email = EmailMessage()
        email.subject = subject
        email.body = message
        email.from_email = from_email
        email.to = [email_to, ]
        email.content_subtype = "html"
        email.send()
        return True
    # Display an error message if something goes wrong.
    except Exception as e:
        return False


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated, UpdateOwnProfile)

    def create(self, request, *args, **kwargs):
        self.permission_classes = (AllowAny,)
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user_data = request.data
            name = user_data['name']
            email = user_data['email']

            # Create User but not active
            user = UserProfile
            a_user = user.objects.create_user(**user_data)

            data = {
                'id': a_user.id
            }

            # Generate Token
            jwt_token = TokenGenerator(data=data).token

            domain = self.request.META['HTTP_HOST']
            url = 'http://{}/{}/?token={}'.format(domain, 'api/registration', jwt_token)

            context = {
                'name': name,
                'url': url
            }

            # Send Email
            subject = 'Welcome {}'.format(name)
            user_mail = email
            message = render_to_string('email_template.html', context)
            from_email = "milonmahato111@gmail.com"
            mail_send(user_mail, subject, message, from_email)

            return Response({'message': 'success'})

        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )


def complete_registration(request):
    token = request.GET.get('token', None)
    jwt_token = TokenGenerator(token=token)
    if jwt_token.is_valid():
        user = UserProfile.objects.filter(id=jwt_token.data['id']).first()
        user.is_active = True
        user.save()

    return render(request, 'verification-done.html', {'data': jwt_token.data['id']})
