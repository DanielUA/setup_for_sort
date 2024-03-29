import os
import sys
import shutil
import pathlib
import tempfile
import datetime
import collections
from threading import Thread

RESULTS_FOLDERS = ("images", "video", "documents", "audio", "archives")


def normalize(file_name: str) -> str:
    reverse_char_map = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'h', 'ґ': 'g',
        'д': 'd', 'е': 'e', 'є': 'ie', 'ж': 'zh', 'з': 'z',
        'и': 'y', 'і': 'i', 'ї': 'yi', 'й': 'i', 'к': 'k',
        'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p',
        'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f',
        'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
        'ь': "'", 'ю': 'iu', 'я': 'ia'
    }
    
    for key, value in reverse_char_map.items():
        file_name = file_name.replace(key, value)

    return file_name


class ProcessThread(Thread):
    def __init__(self, result_path, element, extensions_info):
        super().__init__()
        self.result_path = result_path
        self.element = element
        self.extensions_info = extensions_info

    def run(self):
        if self.element.is_dir():
            self.process_dir()
        else:
            self.process_file()

    def process_dir(self):
        res = False

        if self.element.name not in RESULTS_FOLDERS:
            folder_res = diver(self.result_path, self.element, self.extensions_info)

            if folder_res is False:
                self.element.rmdir()

            res |= folder_res

        return res

    def process_file(self):

        table = (
            ('JPEG', 'PNG', 'JPG', 'SVG'),
            ('AVI', 'MP4', 'MOV', 'MKV'),
            ('DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX'),
            ('MP3', 'OGG', 'WAV', 'AMR'),
            ('ZIP', 'GZ', 'TAR')
        )

        suffixes_dict = {
            table[i][j]: RESULTS_FOLDERS[i]
            for i in range(len(table))
            for j in range(len(table[i]))
        }

        suffix = self.element.suffix[1:].upper()

        known = suffixes_dict.get(suffix) is not None

        self.extensions_info["known" if known else "unknown"].add(suffix)

        if known:
            dest_folder = suffixes_dict[suffix]
            result_path = self.result_path / dest_folder

            if not result_path.is_dir():
                result_path.mkdir()

            if dest_folder == "archives":
                result_path /= f"{normalize(self.element.stem)}"

                shutil.unpack_archive(
                    str(self.element), str(result_path), self.element.suffix[1:].lower()
                )
            else:
                result_path /= f"{normalize(self.element.stem)}{self.element.suffix}"

                shutil.copy(str(self.element), str(result_path))

        return True


def diver(result_path, folder_path, extensions_info):
    res = False

    if not any(folder_path.iterdir()):
        return res

    threads = []

    for element in folder_path.iterdir():
        thread = ProcessThread(result_path, element, extensions_info)
        thread.start()
        threads.append(thread)
        
    for thread in threads:
        thread.join()
        res |= thread.process_dir() if thread.element.is_dir() else thread.process_file() 

    return res


def post_processor(results_path, extensions_info):
    print(f"Known extensions: {extensions_info['known']}")
    if len(extensions_info['unknown']):
        print(f"Unknown extensions: {extensions_info['unknown']}")

    for folder in results_path.iterdir():
        print(f"{folder.name}:")
        for item in folder.iterdir():
            print(f"\t{item.name}")


def sorter():
    folder_platform_path = sys.argv[1]
    extensions_info = collections.defaultdict(set)
    folder_path = pathlib.Path(folder_platform_path)

    if not folder_path.is_dir():
        raise RuntimeError("error: no such directory")

    with tempfile.TemporaryDirectory() as tmp_platform_path:
        tmp_path = pathlib.Path(tmp_platform_path)

        if diver(tmp_path, folder_path, extensions_info) is False:
            raise RuntimeError("It's empty directory")

        os.makedirs("results", exist_ok=True)

        results_path = pathlib.Path(
            "results/"
            f"result_{datetime.datetime.now().strftime('%d.%m.%y_%H.%M.%S')}"
        )

        shutil.copytree(
            str(tmp_path),
            str(results_path)
        )

    post_processor(results_path, extensions_info)


if __name__ == "__main__":
    sorter()
