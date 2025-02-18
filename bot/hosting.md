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

amvera-panarini-cnpg-namehuntdb-rw # для чтения/записи в БД домен

namehuntbot-panarini.amvera.io -- домен для вебхука
amvera-panarini-cnpg-namehuntdb-rw.amvera.io

<project_name>-<username>.db-msk0.amvera.tech
namehuntdb-panarini.db-msk0.amvera.tech -- DBeaver

curl "https://api.telegram.org/bot7289285845:AAFqSMaDwrpCPF92MP2IV4igpKndiGVnank/getWebhookInfo"


Invoke-WebRequest -Uri "https://namehuntbot-panarini.amvera.io/webhook"


curl -X POST "https://api.telegram.org/bot7289285845:AAFqSMaDwrpCPF92MP2IV4igpKndiGVnank/deleteWebhook"

curl -X POST "https://api.telegram.org/bot7289285845:AAFqSMaDwrpCPF92MP2IV4igpKndiGVnank/deleteWebhook?drop_pending_updates=true"



git add .
git commit -m "..."
git push origin main
git push amvera main:master
