from llama_index.core import SimpleDirectoryReader


class PDFLoader:
    def load(self, pdf_path: str):
        reader = SimpleDirectoryReader(input_files=[pdf_path])
        return reader.load_data()

    def load_multiple(self, pdf_paths: list[str]):
        reader = SimpleDirectoryReader(input_files=pdf_paths)
        return reader.load_data()
