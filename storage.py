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
        self._safe_write_lines(self.user_file, [",".join(values)])

    def read_simplehist(self):
        try:
            lines = self._safe_open_lines(self.simplehist_file)
            result = []
            for line in lines:
                if line:
                    (
                        hist_no,
                        hist_datetime,
                        hist_status,
                        hist_name
                    ) = line.split(",", 3)
                    result.append({
                        "hist_no": int(hist_no),
                        "hist_datetime": hist_datetime,
                        "hist_status": hist_status,
                        "hist_name": hist_name
                    })
                    del line
            del lines
            return result
        except OSError:  # FileNotFoundError の代わりに OSError を使用
            return []

    def write_simplehist(self, data):
        lines = [
            f"{entry['hist_no']},{entry['hist_datetime']},{entry['hist_status']},{entry['hist_name']}"
            for entry in data
        ]
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
                            if field.endswith("_no"):
                                entry[field] = int(values[i])
                            else:
                                entry[field] = values[i]
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
        with open(self.jobhist_file, "w") as file:
            for entry in data:
                gc.collect()
                # カンマを全角に変換してエスケープ
                job_name = entry['job_name'].replace(",", "、")
                file.write(f"{entry['job_no']},{job_name},")
                lines = entry['job_description'].split('\n')
                for i, line in enumerate(lines):
                    safe_line = line.replace(",", "、")
                    if i == len(lines) - 1:
                        file.write(safe_line)
                    else:
                        file.write(safe_line + "<br>")
                file.write("\n")

    def read_portrait(self):
        return self._read_csv_with_fields(
            self.portrait_file,
            ("portrait_no", "portrait_url", "portrait_summary")
        )

    def write_portrait(self, data):
        with open(self.portrait_file, "w") as file:
            for entry in data:
                portsummary = entry['portrait_summary'].replace("\n", "<br>").replace(",", "、")
                porturlsafe = entry['portrait_url'].replace(",", "、")
                file.write(
                    f"{entry['portrait_no']},"
                    f"{porturlsafe},"
                    f"{portsummary}\n"
                )

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
