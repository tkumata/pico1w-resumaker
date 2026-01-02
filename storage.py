import uos
import gc


class Storage:
    # ユーザー情報のキーを定数として定義
    USER_KEYS = [
        "usr_name", "usr_name_kana", "usr_gender", "usr_birthday",
        "usr_age", "usr_addr", "usr_phone",
        "usr_mobile", "usr_email", "usr_family", "usr_licenses",
        "usr_siboudouki", "usr_hobby", "usr_skill", "usr_access"
    ]

    # 改行をBRタグに置換するキーのセット
    KEYS_TO_REPLACE = {"usr_licenses",
                       "usr_siboudouki", "usr_hobby", "usr_skill"}

    def __init__(self):
        self.data_dir = "/data"
        self.user_file = f"{self.data_dir}/user.csv"
        self.simplehist_file = f"{self.data_dir}/simplehist.csv"
        self.jobhist_file = f"{self.data_dir}/jobhist.csv"
        self.portrait_file = f"{self.data_dir}/portrait.csv"
        try:
            uos.mkdir(self.data_dir)
        except OSError:
            pass

    def read_user(self):
        try:
            lines = self._safe_open_lines(self.user_file)
            if not lines or lines[0] == "":
                return {}
            return dict(zip(self.USER_KEYS, lines[0].split(",")))
        except OSError:  # FileNotFoundError の代わりに OSError を使用
            return {}

    def write_user(self, data):
        values = [self._sanitize_value(key, data.get(key, ""))
                  for key in self.USER_KEYS]
        # user.csv の各フィールドからカンマを除去（または置換）
        safe_values = [v.replace(",", "、") for v in values]
        self._safe_write_lines(self.user_file, [",".join(safe_values)])

    def read_simplehist(self):
        return self._read_csv_with_fields(
            self.simplehist_file,
            ("hist_no", "hist_datetime", "hist_status", "hist_name")
        )

    def write_simplehist(self, data):
        lines = []
        for entry in data:
            # カンマを置換してCSV構造を保護
            datetime = str(entry['hist_datetime']).replace(",", "、")
            status = str(entry['hist_status']).replace(",", "、")
            name = str(entry['hist_name']).replace(",", "、")
            lines.append(f"{entry['hist_no']},{datetime},{status},{name}")
        
        gc.collect()
        self._safe_write_lines(self.simplehist_file, lines)

    def _read_csv_with_fields(self, filepath, field_names):
        """
        CSV ファイルを読み込む共通メソッド
        field_names: フィールド名のタプル (例: ("job_no", "job_name", "job_description"))
        """
        try:
            with open(filepath, "r") as file:
                result = []
                while True:
                    line = file.readline()
                    if not line:
                        break
                    line = line.strip()
                    if line:
                        # 最後のフィールドにカンマが含まれることを想定
                        values = line.split(",", len(field_names) - 1)
                        entry = {}
                        for i, field in enumerate(field_names):
                            if i < len(values):
                                if field.endswith("_no"):
                                    try:
                                        entry[field] = int(values[i])
                                    except ValueError:
                                        entry[field] = 0
                                else:
                                    entry[field] = values[i]
                            else:
                                entry[field] = ""
                        result.append(entry)
                    del line
                return result
        except OSError:
            return []

    def read_jobhist(self):
        return self._read_csv_with_fields(
            self.jobhist_file,
            ("job_no", "job_name", "job_description")
        )

    def write_jobhist(self, data):
        lines = []
        for entry in data:
            # カンマを置換し、改行を<br>に変換
            job_name = str(entry['job_name']).replace(",", "、")
            desc = str(entry['job_description']).replace("\n", "<br>").replace(",", "、")
            lines.append(f"{entry['job_no']},{job_name},{desc}")
        
        gc.collect()
        self._safe_write_lines(self.jobhist_file, lines)

    def read_portrait(self):
        return self._read_csv_with_fields(
            self.portrait_file,
            ("portrait_no", "portrait_url", "portrait_summary")
        )

    def write_portrait(self, data):
        lines = []
        for entry in data:
            url = str(entry['portrait_url']).replace(",", "、")
            summary = str(entry['portrait_summary']).replace("\n", "<br>").replace(",", "、")
            lines.append(f"{entry['portrait_no']},{url},{summary}")
        
        gc.collect()
        self._safe_write_lines(self.portrait_file, lines)

    def _safe_open_lines(self, filepath):
        try:
            with open(filepath, "r") as file:
                return file.read().strip().split("\n")
        except OSError:
            return []

    def _safe_write_lines(self, filepath, lines):
        with open(filepath, "w") as file:
            file.write("\n".join(lines))

    def _sanitize_value(self, key, value):
        if value is None:
            return ""
        if key in self.KEYS_TO_REPLACE:
            return value.replace("\n", "<br>")
        return value
