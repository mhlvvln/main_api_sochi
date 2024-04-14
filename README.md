Основной Backend-сервер.

Принцип работы: 

1. Авторизация проходит по Bearer-токену.
2. Определяется доступность пользователя к методу(валидация по роли).


Логическая составляющая:
1. Пользователь загружает заявку о повышении цены
2. Прикрепленные геоданные получают адрес, проверяют из данного файла на подписание меморандума
3. Проверяется фотография на то, что цена действительно выше рекомендованной
4. Создается заявка

Изменение статуса заявки:
1. Работник загружает фотографию
2. Она сравнивается с уже созданной записью, что цена меньше
3. Сравнивается, что цена меньше рекомендованной(снова проходит через модель)
4. Если категория совпадает, то меняется статус
5. Если категория или цена не валидны - статус не меняется
