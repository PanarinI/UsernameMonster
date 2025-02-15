

# === 6️⃣ Запуск ===
if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        app = loop.run_until_complete(main())  # Запускаем бота

        if not IS_LOCAL:
            print(f"🚀 Попытка запустить сервер на {WEBAPP_HOST}:{WEBAPP_PORT}")
            logging.info(f"🚀 Попытка запустить сервер на {WEBAPP_HOST}:{WEBAPP_PORT}")
            web.run_app(app, host="0.0.0.0", port=80, access_log=logging)

        # 🔥 Держим контейнер живым
        while True:
            print("♻️ Контейнер работает, Amvera не убивай его!")
            time.sleep(30)

    except Exception as e:
        error_message = traceback.format_exc()
        logging.error(f"❌ Глобальная ошибка: {e}\n{error_message}")
