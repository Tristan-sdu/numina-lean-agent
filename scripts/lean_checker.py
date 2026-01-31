"""
Lean file checking utilities.
"""

import subprocess
from pathlib import Path
from typing import List, Tuple
from multiprocessing import Pool, cpu_count


def find_lean_files(folder_path: str | Path) -> List[Path]:
    """
    Recursively find all .lean files in a folder.

    Args:
        folder_path: Path to the folder to search

    Returns:
        Sorted list of .lean file paths

    中文说明：递归遍历指定目录，收集所有 .lean 文件路径并按排序返回。
    """
    folder = Path(folder_path)
    if not folder.exists():
        raise FileNotFoundError(f"Folder does not exist: {folder_path}")

    if not folder.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {folder_path}")

    lean_files = []
    for file_path in folder.rglob("*.lean"):
        if file_path.is_file():
            lean_files.append(file_path)

    return sorted(lean_files)


def find_lean_project_root(file_path: Path) -> Path:
    """
    Find the Lean project root (directory containing lean-toolchain).

    Args:
        file_path: Path to a file or directory

    Returns:
        Project root path, or the file's parent if not found

    中文说明：向上查找包含 lean-toolchain 的目录，若未找到则返回原路径的父目录。
    """
    current = file_path.parent if file_path.is_file() else file_path
    while current != current.parent:  # Until reaching root
        lean_toolchain = current / "lean-toolchain"
        if lean_toolchain.exists():
            return current
        current = current.parent
    # If not found, return file's parent directory
    return file_path.parent if file_path.is_file() else file_path


def check_lean_file(file_path: Path) -> Tuple[bool, bool, str, str]:
    """
    Check a single .lean file for errors and sorry warnings.

    Args:
        file_path: Path to the .lean file

    Returns:
        (has_error, has_sorry_warning, stdout, stderr)

    中文说明：使用 lake env lean 检查单个 .lean 文件，返回是否有错误/包含 sorry 以及输出。
    """
    try:
        # Find project root containing lean-toolchain
        project_root = find_lean_project_root(file_path)

        # Use lake env lean command to check the file
        result = subprocess.run(
            ["lake", "env", "lean", str(file_path)],
            capture_output=True,
            text=True,
            timeout=60,  # 60 second timeout
            cwd=str(project_root),  # Run in project root
        )

        stdout = result.stdout
        stderr = result.stderr

        # Check for errors
        has_error = (
            "error" in stdout.lower()
            or "error" in stderr.lower()
            or result.returncode != 0
        )

        # Check for sorry warnings
        has_sorry_warning = "sorry" in stdout.lower() or "sorry" in stderr.lower()

        return has_error, has_sorry_warning, stdout, stderr

    except subprocess.TimeoutExpired:
        return True, False, "", "Check timed out (60s)"
    except Exception as e:
        return True, False, "", f"Execution error: {str(e)}"


def _check_wrapper(file_path: Path) -> Tuple[Path, bool, bool, str, str]:
    """
    Wrapper function for multiprocessing.

    Returns:
        (file_path, has_error, has_sorry_warning, stdout, stderr)

    中文说明：供多进程调用的包装函数，返回文件路径及检查结果。
    """
    has_error, has_sorry_warning, stdout, stderr = check_lean_file(file_path)
    return (file_path, has_error, has_sorry_warning, stdout, stderr)


def check_lean_files_parallel(
    lean_files: List[Path], num_proc: int = None
) -> List[Tuple[Path, bool, bool, str, str]]:
    """
    Check multiple .lean files in parallel.

    Args:
        lean_files: List of .lean file paths
        num_proc: Number of parallel processes (default: CPU count)

    Returns:
        List of (file_path, has_error, has_sorry_warning, stdout, stderr)

    中文说明：并行检查多个 .lean 文件，返回每个文件的错误、sorry 警告与输出信息。
    """
    if num_proc is None:
        num_proc = cpu_count()

    with Pool(processes=num_proc) as pool:
        results = pool.map(_check_wrapper, lean_files)

    return results


def check_folder(
    folder_path: str | Path, num_proc: int = None
) -> Tuple[bool, List[Path], List[Path]]:
    """
    Check all .lean files in a folder.

    Args:
        folder_path: Path to the folder
        num_proc: Number of parallel processes

    Returns:
        (all_passed, error_files, sorry_files)

    中文说明：检查文件夹内所有 .lean 文件，返回整体是否通过、错误文件列表和含 sorry 的文件列表。
    """
    lean_files = find_lean_files(folder_path)
    if not lean_files:
        return True, [], []

    results = check_lean_files_parallel(lean_files, num_proc)

    error_files = []
    sorry_files = []

    for file_path, has_error, has_sorry_warning, _, _ in results:
        if has_error:
            error_files.append(file_path)
        elif has_sorry_warning:
            sorry_files.append(file_path)

    all_passed = len(error_files) == 0 and len(sorry_files) == 0
    return all_passed, error_files, sorry_files
