from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.throttling import AnonRateThrottle
from rest_framework.throttling import ScopedRateThrottle


from .models import Achievement, Cat, User
from .pagination import CatsPagination, CustomPagination
from .permissions import OwnerOrReadOnly, ReadOnly
from .serializers import AchievementSerializer, CatSerializer, UserSerializer
from .throttling import WorkingHoursRateThrottle


class CatViewSet(viewsets.ModelViewSet):
    queryset = Cat.objects.all()
    serializer_class = CatSerializer
    # Анонимным GET-запросом можно получить информацию о котиках.
    # Все остальное закрыто.
    # permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    # Кастомный класс permisions:
    permission_classes = (OwnerOrReadOnly,)
    # Подключили класс AnonRateThrottle
    # throttle_classes = (AnonRateThrottle,)
    # Если кастомный тротлинг-класс вернёт True - запросы будут обработаны
    # Если он вернёт False - все запросы будут отклонены
    throttle_classes = (WorkingHoursRateThrottle, ScopedRateThrottle)
    # Для любых пользователей установим кастомный лимит 1 запрос в минуту
    throttle_scope = 'low_request'
    # Игнорируем pagination указанную в settings.
    # pagination_class = None  # или ставим PageNumberPagination
    # pagination_class = LimitOffsetPagination
    # Или кастомный пагинатор
    pagination_class = CatsPagination

    def get_permissions(self):

        '''Теперь при GET-запросе информации о конкретном котике доступ
        будет определяться пермишеном ReadOnly: запросы будут разрешены всем.
        При остальных запросах доступ будет определять
        пермишен OwnerOrReadOnly.'''

        # Если в GET-запросе требуется получить информацию об объекте
        if self.action == 'retrieve':
            # Вернём обновлённый перечень используемых пермишенов
            return (ReadOnly(),)
        # Для остальных ситуаций оставим текущий перечень пермишенов.
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class AchievementViewSet(viewsets.ModelViewSet):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer
