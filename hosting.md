amvera 

внутреннее доменное имя amvera-panarini-run-namehuntbot

git remote add amvera https://git.amvera.ru/<имя-пользователя>/<транслитерированное-имя-проекта>

git remote add amvera https://git.amvera.ru/PanarinI/namehuntbot # один раз создаем

git push amvera main:master # если не работае git push amvera master


Верная последовательность
git add . # Добавляем все сделанные изменения в данной папке в список проиндексированных
git commit -m "Описание сделанных изменений"
git push amvera master