from bot.utils.base_utils import get_text


class MainMenuTexts:
    _language_code: str
    
    def __init__(self, language_code: str):
        self._language_code = language_code
        
    
    def get_start_menu_text(self) -> str:
        return get_text('start_menu', 'start_menu', self._language_code)
    
    def get_choose_language_text(self) -> str:
        return get_text('start_menu', 'choose_language', self._language_code)