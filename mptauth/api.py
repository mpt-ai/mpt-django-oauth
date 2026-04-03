from mptauth.models import Account
from rest_framework import serializers, viewsets, mixins, permissions, response, status
from rest_framework.decorators import action
from rest_framework import permissions
from rest_framework import routers

class AccountSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField('get_username')
    is_staff = serializers.SerializerMethodField()
    is_superuser = serializers.SerializerMethodField()
    class Meta:
        model = Account
        fields = '__all__'
    
    def get_username(self, obj):
        return obj.user.username
    
    def get_is_staff(self, obj) -> bool:
        return obj.user.is_staff
    
    def get_is_superuser(self, obj) -> bool:
        return obj.user.is_superuser

class AccountViewsets(viewsets.GenericViewSet,
                      mixins.RetrieveModelMixin):
    
    def get_permissions(self):
        self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def get_serializer_class(self):
        return AccountSerializer
    
    def get_queryset(self):
        return Account.objects.none()
    
    @action(methods=['GET'], detail=False)
    def me(self, request, *args, **kwargs):
        account = Account.objects.get(user=request.user)
        res = AccountSerializer(account).data
        return response.Response(res, status=status.HTTP_200_OK)
    


router = routers.DefaultRouter()
router.register('account', viewset=AccountViewsets, basename='account')