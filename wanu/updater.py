import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from wanu.defines import HAC2L, HACPACK, HACTOOL, TITLEKEY_PATH
from wanu.ticket import TitleKey, store_title_key
from wanu.utils import clear_titlekeys, get_files_with_ext

NCA_EXT = "[nN][cC][aA]"
NSP_EXT = "[nN][sS][pP]"


def update_nsp(
    base_nsp: Path,
    update_nsp: Path,
    outdir: Path,
    program_id: str | None = None,
):
    clear_titlekeys()

    with tempfile.TemporaryDirectory() as base_data_dir, tempfile.TemporaryDirectory() as update_data_dir:
        unpack_nsp(base_nsp, Path(base_data_dir))
        unpack_nsp(update_nsp, Path(update_data_dir))
        ...

    ...


def unpack_nsp(nsp: Path, to: Path) -> None:
    assert nsp.is_file()
    assert to.is_dir()

    subprocess.run([HACTOOL, "-t", "pfs0", nsp, to], check=True)


def unpack_update_nca(
    base_nca: Path, update_nca: Path, romfs_dir: Path, exefs_dir: Path
) -> None:
    assert base_nca.is_file()
    assert update_nca.is_file()
    assert romfs_dir.is_dir()
    assert exefs_dir.is_dir()

    subprocess.run(
        [
            HAC2L,
            "--basenca",
            base_nca,
            update_nca,
            "--romfsdir",
            romfs_dir,
            "--exefsdir",
            exefs_dir,
        ],
        check=True,
    )


def create_meta_nca(
    program_nca: Path,
    control_nca: Path,
    program_id: str,
    romfs_dir: Path,
    exefs_dir: Path,
    outdir: Path,
    keyfile: Path = TITLEKEY_PATH,
) -> Path:
    with tempfile.TemporaryDirectory() as temp_outdir:
        subprocess.run(
            [
                HACPACK,
                "--keyset",
                keyfile,
                "--type",
                "nca",
                "--ncatype",
                "meta",
                "--titletype",
                "application",
                "--programnca",
                program_nca,
                "--controlnca",
                control_nca,
                "--titleid",
                program_id,
                "--outdir",
                temp_outdir,
            ],
        )

        for nca in get_files_with_ext(Path(temp_outdir), NCA_EXT):
            dest = outdir.joinpath(nca.name)
            shutil.move(nca, dest)
            return dest

    raise Exception("Failed to generate Meta NCA")


def pack_program(
    program_id: str,
    romfs_dir: Path,
    exefs_dir: Path,
    outdir: Path,
    keyfile: Path = TITLEKEY_PATH,
) -> Path:
    with tempfile.TemporaryDirectory() as temp_outdir:
        subprocess.run(
            [
                HACPACK,
                "--keyset",
                keyfile,
                "--type",
                "nca",
                "--ncatype",
                "program",
                "--plaintext",
                "--exefsdir",
                exefs_dir,
                "--romfsdir",
                romfs_dir,
                "--titleid",
                program_id,
                "--outdir",
                temp_outdir,
            ]
        )

        for nca in get_files_with_ext(Path(temp_outdir), NCA_EXT):
            dest = outdir.joinpath(nca.name)
            shutil.move(nca, dest)
            return dest

    raise Exception("Failed to pack FS files to NCA")
