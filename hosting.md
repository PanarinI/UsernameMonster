amvera 

внутреннее доменное имя amvera-panarini-run-namehuntbot

git remote add amvera https://git.amvera.ru/<имя-пользователя>/<транслитерированное-имя-проекта>

git remote add amvera https://git.amvera.ru/PanarinI/namehuntbot # один раз создаем

git push amvera main:master # если не работае git push amvera master


Верная последовательность
git add . # Добавляем все сделанные изменения в данной папке в список проиндексированных
git commit -m "Описание сделанных изменений"
git push amvera main:master


namehunt_db # название БД

amvera-panarini-cnpg-namehuntdb-rw # для чтения/записи ХОСТ

F:\PostgreSQL\bin\psql.exe -h amvera-panarini-cnpg-namehuntdb-rw -U PanarinI -d namehunt_db -W

amvera-panarini-cnpg-namehuntdb-rw


namehuntbot-panarini.amvera.io -- домен для вебхука

curl https://api.telegram.org/bot7289285845:AAFqSMaDwrpCPF92MP2IV4igpKndiGVnank/getWebhookInfo -- проверка webhook
 

https://namehuntbot-panarini.amvera.io/bot/7289285845:AAFqSMaDwrpCPF92MP2IV4igpKndiGVnank

curl "https://api.telegram.org/bot7289285845:AAFqSMaDwrpCPF92MP2IV4igpKndiGVnank/setWebhook?url=https://namehuntbot-panarini.amvera.io/bot/7289285845:AAFqSMaDwrpCPF92MP2IV4igpKndiGVnank"
