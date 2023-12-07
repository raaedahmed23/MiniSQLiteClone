class static(object):
    def __new__(cls, *args, **kwargs):
        raise RuntimeError('%s new keyword invalid, static class' % cls)

class Settings(static):
    prompt = "davisql> "
    db_name = "davisDB"

    tbl_ext = ".tbl"
    ndx_ext = '.ndx'
    
    data_dir = "data"
    exec_path = ""
    
    page_size = 512
    exit = False

    @staticmethod
    def line(rep: str, n_rep: int) -> str:
        return "".join([rep]*n_rep)

    @classmethod
    def set_exec_path(cls, value: str):
        cls.exec_path = value

    @classmethod
    def set_data_dir(cls, value: str):
        cls.data_dir = value

    @classmethod
    def set_db_name(cls, value: str):
        cls.db_name = value

    @classmethod
    def set_tbl_ext(cls, value : str):
        cls.tbl_ext = value
    
    @classmethod
    def set_ndx_ext(cls, value : str):
        cls.idx_ext = value

    @classmethod
    def get_prompt(cls, value : str):
        cls.prompt = value
    
    @classmethod
    def set_exit(cls,value : bool):
        cls.exit = value

    @classmethod
    def get_exec_path(cls) -> str:
        return cls.exec_path

    @classmethod
    def get_data_dir(cls) -> str:
        return cls.data_dir

    @classmethod
    def get_db_file(cls) -> str:
        return cls.db_file
    
    @classmethod
    def get_db_name(cls) -> str:
        return cls.db_name

    @classmethod
    def get_tbl_ext(cls) -> str:
        return cls.tbl_ext
    
    @classmethod
    def get_ndx_ext(cls) -> str:
        return cls.ndx_ext

    @classmethod
    def get_prompt(cls) -> str:
        return cls.prompt

    @classmethod
    def is_exit(cls) -> bool:
        return cls.exit
   
    @classmethod
    def get_page_size(cls) -> int:
        return cls.page_size

    
