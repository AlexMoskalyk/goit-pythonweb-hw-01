import argparse
import asyncio
import logging
import shutil
from pathlib import Path

# Налаштування логування
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def copy_file(file: Path, output_folder: Path):
    """Асинхронне копіювання файлу у відповідну підпапку на основі розширення."""
    try:
        if not file.is_file():
            return

        extension = (
            file.suffix.lower().strip(".") or "unknown"
        )  # Якщо без розширення - в 'unknown'
        target_dir = output_folder / extension
        target_dir.mkdir(
            parents=True, exist_ok=True
        )  # Створення папки, якщо вона не існує
        target_file = target_dir / file.name

        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, shutil.copy2, file, target_file)

        logger.info(f"Файл {file.name} скопійовано в {target_dir}")
    except Exception as e:
        logger.error(f"Помилка копіювання {file.name}: {e}")


async def read_folder(source_folder: Path, output_folder: Path):
    """Асинхронно рекурсивно читає файли з вихідної папки та передає їх у функцію копіювання."""
    tasks = []
    for file in source_folder.rglob("*"):  # Рекурсивно шукаємо всі файли
        if file.is_file():
            tasks.append(copy_file(file, output_folder))

    if tasks:
        await asyncio.gather(*tasks)  # Запускаємо всі задачі одночасно


def main():
    parser = argparse.ArgumentParser(
        description="Асинхронне сортування файлів за розширенням."
    )
    parser.add_argument("source_folder", type=str, help="Шлях до вихідної папки")
    parser.add_argument("output_folder", type=str, help="Шлях до цільової папки")

    args = parser.parse_args()
    source_folder = Path(args.source_folder).resolve()
    output_folder = Path(args.output_folder).resolve()

    if not source_folder.exists() or not source_folder.is_dir():
        logger.error(f"Вихідна папка '{source_folder}' не існує або не є директорією.")
        return

    logger.info(f"Розпочато сортування файлів з {source_folder} в {output_folder}")
    asyncio.run(read_folder(source_folder, output_folder))
    logger.info("Сортування завершено.")


if __name__ == "__main__":
    main()
