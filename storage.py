import uos


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
            with open(self.user_file, "r") as file:
                lines = file.read().strip().split("\n")
                if not lines or lines[0] == "":
                    return {}
                return dict(zip(self.USER_KEYS, lines[0].split(",")))
        except OSError:  # FileNotFoundError の代わりに OSError を使用
            return {}

    def write_user(self, data):
        with open(self.user_file, "w") as file:
            values = [
                data.get(key, "").replace("\n", "<br>")
                if key in self.KEYS_TO_REPLACE
                else data.get(key, "")
                for key in self.USER_KEYS
            ]
            file.write(",".join(values))

    def read_simplehist(self):
        try:
            with open(self.simplehist_file, "r") as file:
                lines = file.read().strip().split("\n")
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
                return result
        except OSError:  # FileNotFoundError の代わりに OSError を使用
            return []

    def write_simplehist(self, data):
        with open(self.simplehist_file, "w") as file:
            for entry in data:
                file.write(
                    f"{entry['hist_no']},"
                    f"{entry['hist_datetime']},"
                    f"{entry['hist_status']},"
                    f"{entry['hist_name']}\n"
                )

    def read_jobhist(self):
        try:
            with open(self.jobhist_file, "r") as file:
                lines = file.read().strip().split("\n")
                result = []
                for line in lines:
                    if line:
                        job_no, name, desc = line.split(",", 2)
                        result.append({
                            "job_no": int(job_no),
                            "job_name": name,
                            "job_description": desc
                        })
                return result
        except OSError:  # FileNotFoundError の代わりに OSError を使用
            return []

    def write_jobhist(self, data):
        with open(self.jobhist_file, "w") as file:
            for entry in data:
                jobdesc = entry['job_description'].replace("\n", "<br>")
                file.write(
                    f"{entry['job_no']},"
                    f"{entry['job_name']},"
                    f"{jobdesc}\n"
                )

    def read_portrait(self):
        try:
            with open(self.portrait_file, "r") as file:
                lines = file.read().strip().split("\n")
                result = []
                for line in lines:
                    if line:
                        (
                            portrait_no,
                            portrait_url,
                            portrait_summary
                        ) = line.split(",", 2)
                        result.append({
                            "portrait_no": int(portrait_no),
                            "portrait_url": portrait_url,
                            "portrait_summary": portrait_summary
                        })
                return result
        except OSError:
            return []

    def write_portrait(self, data):
        with open(self.portrait_file, "w") as file:
            for entry in data:
                portsummary = entry['portrait_summary'].replace("\n", "<br>")
                file.write(
                    f"{entry['portrait_no']},"
                    f"{entry['portrait_url']},"
                    f"{portsummary}\n"
                )
