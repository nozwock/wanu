if __name__ == "__main__":
    import typer

    from wanu.updater import update_nsp
    from wanu.utils import check_aarch64_linux

    check_aarch64_linux()

    typer.run(update_nsp)
