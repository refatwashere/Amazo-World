from amazo_bot.telegram_app import build_application


def main() -> None:
    app = build_application()
    app.run_polling()


if __name__ == "__main__":
    main()
