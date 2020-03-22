from rest_framework import permissions
from .serializers import *
from rest_framework import viewsets, status
from rest_framework.response import Response


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerialize
    permission_classes = [permissions.IsAuthenticated]

    def parse_data_post(self, data):
        """
        Parse data da request para um Dict no formato que o serializer precisa para um POST / PUT
        """
        django_user_fields = ['username', 'email', 'password']
        data_user = {}
        data_django_user = {}

        for key in data:
            if key in django_user_fields:
                data_django_user[key] = data.get(key)
            else:
                data_user[key] = data.get(key)

        data_user['user'] = data_django_user
        return data_user

    def parse_data_get(self, data):
        """
        Parse data para alterar formato de saida dos dados de um serializer em um GET
        """
        data = {**data}  # data é imutável por padrao, entao preciso cria outro dict
        user_django = data.pop('user', {})
        user_django.pop('id', None)  # remove o id do usuario do django
        return {**data, **user_django}

    def list(self, request, *args, **kwargs):
        """
        Sobrecreve o comportamento padrao para utilizar os dados com o parse
        """
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        data = []
        for user in serializer.data:
            data.append(self.parse_data_get(user))
        return Response(data)

    def retrieve(self, request, *args, **kwargs):
        """
        Sobrecreve o comportamento padrao para utilizar os dados com o parse
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = self.parse_data_get(serializer.data)
        return Response(data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        data = self.parse_data_post(request.data)
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        data = self.parse_data_get(request.data)
        return Response(data)

    def create(self, request, *args, **kwargs):
        """
        Sobrecreve o comportamento padrao para utilizar os dados com o parse
        """
        data = self.parse_data_post(request.data)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = self.parse_data_get(request.data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)
