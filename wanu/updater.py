import os
import re
import shutil
import subprocess
import tempfile
from enum import Enum
from pathlib import Path

from wanu.defines import HAC2L, HACPACK, HACTOOL, PRODKEYS_PATH
from wanu.ticket import TitleKey, clear_titlekeys, store_title_key
from wanu.utils import get_files_with_ext

NCA_EXT = "[nN][cC][aA]"
NSP_EXT = "[nN][sS][pP]"
TIK_EXT = "[tT][iI][kK]"

PROGRAMID_LEN = 16
CONTENT_TYPE_PAT = re.compile(r"Content\s*Type:\s*(\S*)")


def update_nsp(
    base_nsp: Path,
    update_nsp: Path,
    outdir: Path,
    program_id: str | None = None,
) -> Path:
    assert base_nsp.is_file()
    assert update_nsp.is_file()

    clear_titlekeys()

    base_data_dir = tempfile.TemporaryDirectory()
    update_data_dir = tempfile.TemporaryDirectory()
    fs_dir = tempfile.TemporaryDirectory()
    nca_dir = tempfile.TemporaryDirectory()

    try:
        # Extracting pfs0
        unpack_nsp(base_nsp, Path(base_data_dir.name))
        unpack_nsp(update_nsp, Path(update_data_dir.name))

        base_title_key = TitleKey.new(
            next(get_files_with_ext(Path(base_data_dir.name), TIK_EXT))
        )
        update_title_key = TitleKey.new(
            next(get_files_with_ext(Path(update_data_dir.name), TIK_EXT))
        )

        # Storing TitleKeys file
        store_title_key(filter(None, [base_title_key, update_title_key]))

        base_nca = next(
            (
                nca
                for nca in get_files_with_ext(Path(base_data_dir.name), NCA_EXT)
                if get_content_type(nca) == ContentType.Program.name
            ),
            None,
        )
        assert base_nca is not None

        update_nca = next(
            (
                nca
                for nca in get_files_with_ext(Path(update_data_dir.name), NCA_EXT)
                if get_content_type(nca) == ContentType.Program.name
            ),
            None,
        )
        assert update_nca is not None

        control_nca = next(
            (
                nca
                for nca in get_files_with_ext(Path(update_data_dir.name), NCA_EXT)
                if get_content_type(nca) == ContentType.Control.name
            ),
            None,
        )
        assert control_nca is not None

        romfs_dir = Path(fs_dir.name).joinpath("romfs")
        exefs_dir = Path(fs_dir.name).joinpath("exefs")

        try:
            # Unpacking FS files from NCA
            unpack_update_nca(base_nca, update_nca, romfs_dir, exefs_dir)
        except Exception:
            pass

        assert base_title_key is not None
        if program_id is None:
            program_id = base_title_key.rights_id
        program_id = program_id[:PROGRAMID_LEN]

        # Move Control NCA before cleanup
        os.makedirs(nca_dir.name, exist_ok=True)
        old_control_nca = control_nca
        control_nca = Path(nca_dir.name).joinpath(Path(control_nca).name)
        shutil.move(old_control_nca, control_nca)
        del old_control_nca

        # Cleanup
        base_data_dir.cleanup()
        update_data_dir.cleanup()

        # Packing FS files to NCA
        patched_nca = pack_program_nca(
            program_id, romfs_dir, exefs_dir, Path(nca_dir.name)
        )

        # Cleanup
        fs_dir.cleanup()

        meta_nca = create_meta_nca(
            program_id, patched_nca, control_nca, Path(nca_dir.name)
        )

        patched_nsp = pack_nsp(program_id, Path(nca_dir.name), outdir)

    finally:
        base_data_dir.cleanup()
        update_data_dir.cleanup()
        fs_dir.cleanup()
        nca_dir.cleanup()

    return patched_nsp


def unpack_nsp(nsp: Path, to: Path) -> None:
    assert nsp.is_file()
    assert PRODKEYS_PATH.is_file()

    subprocess.run([HACTOOL, "-t", "pfs0", nsp, "--outdir", to], check=True)


def unpack_update_nca(
    base_nca: Path, update_nca: Path, romfs_dir: Path, exefs_dir: Path
) -> None:
    assert base_nca.is_file()
    assert update_nca.is_file()
    assert PRODKEYS_PATH.is_file()

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
    program_id: str,
    program_nca: Path,
    control_nca: Path,
    outdir: Path,
    keyfile: Path = PRODKEYS_PATH,
) -> Path:
    assert program_nca.is_file()
    print(control_nca)
    assert control_nca.is_file()
    assert keyfile.is_file()

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


def pack_program_nca(
    program_id: str,
    romfs_dir: Path,
    exefs_dir: Path,
    outdir: Path,
    keyfile: Path = PRODKEYS_PATH,
) -> Path:
    assert romfs_dir.is_dir()
    assert exefs_dir.is_dir()
    assert keyfile.is_file()

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


def pack_nsp(
    program_id: str,
    nca_dir: Path,
    outdir: Path,
    keyfile: Path = PRODKEYS_PATH,
):
    assert nca_dir.is_dir()
    assert keyfile.is_file()

    subprocess.run(
        [
            HACPACK,
            "--keyset",
            keyfile,
            "--type",
            "nsp",
            "--ncadir",
            nca_dir,
            "--titleid",
            program_id,
            "--outdir",
            outdir,
        ],
        check=True,
    )

    packed_nsp = outdir.joinpath(f"{program_id}.nsp")
    if packed_nsp.is_file():
        return packed_nsp

    raise Exception("Encountered an error while packing NCAs to NSP")


class ContentType(Enum):
    Program = 0x00
    Meta = 0x01
    Control = 0x02
    Manual = 0x03
    Data = 0x04
    PublicData = 0x05


def get_content_type(rom: Path) -> str | None:
    assert rom.is_file()
    assert PRODKEYS_PATH.is_file()
    output = str(
        subprocess.run(
            [HAC2L, rom], capture_output=True, universal_newlines=True
        ).stdout
    )
    content_type = CONTENT_TYPE_PAT.search(output)
    if content_type:
        return content_type.group(1).strip()
    return None
