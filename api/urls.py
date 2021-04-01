from rest_framework import routers

from api.views import  AccountViewSet, TransactionViewSet, CategoryViewSet, AccountTypeViewSet, \
    GoalViewSet, UserViewSet

router = routers.SimpleRouter()
router.register(r'users', UserViewSet)
router.register(r'accounts', AccountViewSet)
router.register(r'transactions', TransactionViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'accountType', AccountTypeViewSet)
router.register(r'goals', GoalViewSet)
urlpatterns = router.urls
