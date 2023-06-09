def run():
    import typer

    from wanu.updater import update_nsp
    from wanu.utils import validate_system

    validate_system()

    typer.run(update_nsp)


if __name__ == "__main__":
    run()
