from rest_framework import routers

from api.views import UserViewSet, AccountViewSet, TransactionViewSet, CategoryViewSet, AccountTypeViewSet, \
    GoalViewSet, TransferViewSet

router = routers.SimpleRouter()
router.register(r'users', UserViewSet)
router.register(r'accounts', AccountViewSet)
router.register(r'transactions', TransactionViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'accountType', AccountTypeViewSet)
router.register(r'goals', GoalViewSet)
router.register(r'transfers', TransferViewSet)
urlpatterns = router.urls
