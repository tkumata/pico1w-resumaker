"""
軽量フォントクラス（0-9a-zA-Z記号のみ対応）
メモリ使用量を大幅に削減した軽量版
7x7フォントを改善して視認性向上
"""

from .lite_fontdata import lite_font_data, lite_font_table


class LiteFont:
    FTABLESIZE = len(lite_font_table)    # フォントテーブルデータサイズ
    FONT_LEN = 7                         # 1フォントのバイト数
    FONT_TOFU = 0x003f                   # "?"コード（見つからない文字用）

    def __init__(self):
        pass

    #  フォントコード検索
    #  引数   ucode UTF-16 コード
    #  戻り値 該当フォントがある場合 フォントコード(0～FTABLESIZE-1)
    #        該当フォントが無い場合 -1
    def find(self, ucode):
        try:
            return lite_font_table.index(ucode)
        except ValueError:
            return -1

    def isZenkaku(self, ucode):
        # 軽量版では半角文字のみなので常にFalse
        return False

    def han2zen(self, ucode):
        # 軽量版では変換なしでそのまま返す
        return ucode

    #  UTF16文字コードに対応するフォントデータ8バイトを取得する
    #  引数   ucode UTF-16 コード
    #  戻り値: 正常終了 取得したデータ(タプル) 、異常終了 None
    def font(self, utf16, flgz=True):
        code = self.find(utf16)
        if code < 0:  # 該当するフォントが存在しない
            code = self.find(self.FONT_TOFU)  # "?"を返す
            if code < 0:  # "?"も見つからない場合は最初の文字（'0'）を返す
                code = 0
        return lite_font_data[code*self.FONT_LEN:code*self.FONT_LEN+self.FONT_LEN] + (0,)
