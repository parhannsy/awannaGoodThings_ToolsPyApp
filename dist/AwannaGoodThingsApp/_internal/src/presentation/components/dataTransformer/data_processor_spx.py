"""
Data Processor SPX

Duplikasi 1:1 dari script Colab yang digunakan untuk
transformasi data SPX.

Perubahan yang dilakukan:
- Input file berasal dari aplikasi desktop.
- Output file berasal dari Save As dialog.
- Tidak ada perubahan logika transformasi.
"""

import os
import re
import random

import pandas as pd

from datetime import datetime, timedelta


class DataProcessorSPX:

    @staticmethod
    def clean_name(name):
        if pd.isna(name):
            return ""

        name = str(name)
        name = re.split(r'[\(\[\{<<\\/]', name)[0]

        return name.strip()

    @staticmethod
    def normalize_phone_plus62(phone):
        if pd.isna(phone):
            return ""

        phone = str(phone)
        phone = re.sub(r'\D', '', phone)

        if phone.startswith("08"):
            return "+62" + phone[1:]

        elif phone.startswith("62"):
            return "+" + phone

        elif phone.startswith("8"):
            return "+62" + phone

        return phone

    @staticmethod
    def normalize_phone_8(phone):
        if pd.isna(phone):
            return ""

        phone = str(phone)
        phone = re.sub(r'\D', '', phone)

        if phone.startswith("08"):
            return phone[1:]

        elif phone.startswith("62"):
            return phone[2:]

        elif phone.startswith("8"):
            return phone

        return phone

    @staticmethod
    def clean_product_name(product):
        if pd.isna(product):
            return ""

        product = str(product).strip()

        if " - " in product:
            parts = product.split(" - ")

            if len(parts) >= 4:
                return parts[1].strip()

        product = re.sub(
            r'^[A-Z0-9\.]+\s+',
            '',
            product,
            flags=re.IGNORECASE
        )

        if " - " in product:
            product = product.split(" - ")[0]

        product = re.sub(r'\s+\d+$', '', product)

        return product.strip()

    @staticmethod
    def normalize_product_name(product_name):
        if pd.isna(product_name):
            return ""

        product_name = str(product_name).upper().strip()

        if (
            "DOUBLE FOKUS" in product_name
            or "DOUBLEFOCUS" in product_name
        ):
            return "KACAMATA DOUBLE FOKUS"

        elif (
            "MULTIFOKUS" in product_name
            or "MULTIFOCUS" in product_name
        ):
            return "KACAMATA MULTIFOKUS"

        elif (
            "BACA" in product_name
            and "JALAN" in product_name
        ):
            return "KACAMATA BACA & JALAN"

        elif "POLARIZED" in product_name:
            return "KACAMATA POLARIZED"

        elif (
            "SPORTY" in product_name
            or (
                "SPORT" in product_name
                and "ESPORT" not in product_name
            )
        ):
            return "KACAMATA SPORTY PHOTOCHROMIC"

        elif (
            "ANTI RADIASI" in product_name
            or "ANTIRADIASI" in product_name
        ):
            return "KACAMATA ANTI RADIASI"

        elif (
            "KABEL" in product_name
            or "USB" in product_name
        ):
            return "KABEL CASAN HP"

        elif "SALMOGENIX" in product_name:
            return "SALMOGENIX"

        return product_name

    @staticmethod
    def normalize_plus_size(size_text):
        if not size_text or size_text == "-":
            return ""

        size_text = str(size_text)

        size_text = size_text.replace(",", ".")
        size_text = size_text.replace(" ", "")

        if not size_text.startswith("+"):
            size_text = "+" + size_text

        return size_text

    @staticmethod
    def determine_size_from_age(age):
        try:
            age = int(age)
        except:
            return ""

        if 40 <= age <= 42:
            return "+1.00"

        elif 43 <= age <= 47:
            return "+1.25"

        elif 48 <= age <= 49:
            return "+1.75"

        elif 50 <= age <= 54:
            return "+2.00"

        elif 55 <= age <= 57:
            return "+2.50"

        elif 58 <= age <= 59:
            return "+2.25"

        elif 60 <= age <= 64:
            return "+3.00"

        elif age >= 65:
            return "+3.50"

        return ""

    @staticmethod
    def parse_notes_strict(notes):
        size = ""
        age = ""
        color = ""
        valid = False

        if pd.isna(notes):
            return size, age, color, valid

        notes = str(notes).strip()

        if notes.count(",") != 2:
            return size, age, color, valid

        parts = [p.strip() for p in notes.split(",")]

        if len(parts) != 3:
            return size, age, color, valid

        age_raw = parts[0]
        size_raw = parts[1]
        color_raw = parts[2]

        if age_raw != "-":
            try:
                age_val = int(age_raw)

                if 1 <= age_val <= 120:
                    age = str(age_val)
            except:
                pass

        if size_raw != "-":
            size_clean = size_raw.replace(" ", "")

            if re.match(r'^\+?\d+\.?\d*$', size_clean):
                size = DataProcessorSPX.normalize_plus_size(
                    size_clean
                )

        if color_raw != "-":
            color = color_raw.upper().strip()

            if len(color) < 1:
                color = ""

        valid = True

        return size, age, color, valid

    @staticmethod
    def determine_qty(product_name, product_price):
        try:
            price = int(float(product_price))
        except:
            return ""

        product_name = str(product_name).upper()

        if "KABEL" in product_name:
            if 99000 <= price <= 99999:
                return "3 pcs"
            elif 169000 <= price <= 169999:
                return "6 pcs"

        elif "SPORTY" in product_name:
            if 99000 <= price <= 119999:
                return "2 pcs"
            elif 149000 <= price <= 169999:
                return "4 pcs"

        elif "BACA & JALAN" in product_name:
            if 119000 <= price <= 119999:
                return "2 pcs"
            elif 179000 <= price <= 179999:
                return "4 pcs"

        elif "MULTIFOKUS" in product_name:
            if 129000 <= price <= 129999:
                return "2 pcs"
            elif 179000 <= price <= 179999:
                return "4 pcs"

        elif "POLARIZED" in product_name:
            if 129000 <= price <= 129999:
                return "2 pcs"
            elif 179000 <= price <= 179999:
                return "4 pcs"

        elif "DOUBLE FOKUS" in product_name:
            if 99000 <= price <= 99999:
                return "2 pcs"
            elif 179000 <= price <= 179999:
                return "4 pcs"

        elif "ANTI RADIASI" in product_name:
            if 129000 <= price <= 129999:
                return "2 pcs"
            elif 179000 <= price <= 179999:
                return "4 pcs"

        elif "SALMOGENIX" in product_name:
            if 89000 <= price <= 89999:
                return "1 box"
            elif 159000 <= price <= 159999:
                return "2 box"

        return ""

    @staticmethod
    def build_product_1(
        product,
        product_price,
        notes,
        label
    ):
        clean_product = product

        size, age, color, valid = (
            DataProcessorSPX.parse_notes_strict(notes)
        )

        qty = DataProcessorSPX.determine_qty(
            clean_product,
            product_price
        )

        result = []

        result.append(label)
        result.append(clean_product)

        if valid:
            detail_parts = []

            if size:
                detail_parts.append(size)

            if age:
                detail_parts.append(age)

            if color:
                detail_parts.append(color)

            if len(detail_parts) > 0:
                result.append(
                    "(" + " - ".join(detail_parts) + ")"
                )

        if qty:
            result.append(f"({qty})")

        return " - ".join(result)

    @staticmethod
    def extract_qty_only(product_1):
        if pd.isna(product_1):
            return ""

        product_1 = str(product_1)

        match = re.search(
            r'(\d+)\s*(pcs|box)',
            product_1,
            re.IGNORECASE
        )

        if match:
            qty_number = match.group(1)
            return f"{qty_number}pcs"

        return ""

    @staticmethod
    def convert_cod(payment_method):
        if pd.isna(payment_method):
            return "N"

        payment_method = str(payment_method).upper()

        if "COD" in payment_method:
            return "Y"

        return "N"

    @staticmethod
    def nominal_cod(payment_method, gross_revenue):
        if pd.isna(payment_method):
            return 0

        payment_method = str(payment_method).upper()

        if "COD" in payment_method:
            return gross_revenue

        return 0

    @staticmethod
    def process(input_file, output_file):

        df = pd.read_excel(input_file)

        df.columns = (
            df.columns
            .str.strip()
            .str.lower()
        )

        total_data = len(df)

        PERCENT_P = 0.25
        PERCENT_D = 0.33
        PERCENT_A = 0.42

        count_p = round(total_data * PERCENT_P)
        count_d = round(total_data * PERCENT_D)

        count_a = total_data - count_p - count_d

        label_pool = (
            ['(P)'] * count_p +
            ['(D)'] * count_d +
            ['(A)'] * count_a
        )

        random.shuffle(label_pool)

        df["label_produk"] = label_pool

        df["product_normalized"] = (
            df["product"]
            .apply(DataProcessorSPX.clean_product_name)
            .apply(DataProcessorSPX.normalize_product_name)
        )

        output = pd.DataFrame()

        output["nama"] = (
            df["name"]
            .apply(DataProcessorSPX.clean_name)
        )

        output["nomor hp (+62)"] = (
            df["phone"]
            .apply(DataProcessorSPX.normalize_phone_plus62)
        )

        output["nomor hp (8)"] = (
            df["phone"]
            .apply(DataProcessorSPX.normalize_phone_8)
        )

        output["alamat lengkap"] = df["address"]

        output["alamat provinsi"] = (
            df["province"]
            .astype(str)
            .str.upper()
        )

        output["alamat kota"] = (
            df["city"]
            .astype(str)
            .str.upper()
        )

        output["alamat kecamatan"] = (
            df["subdistrict"]
            .astype(str)
            .str.upper()
        )

        output["kode pos"] = df["zip"]

        output["berat (Kg)"] = 1

        output["gross_revenue"] = df["gross_revenue"]

        output["Y/N"] = (
            df["payment_method"]
            .apply(DataProcessorSPX.convert_cod)
        )

        output["nominal COD"] = df.apply(
            lambda row: DataProcessorSPX.nominal_cod(
                row["payment_method"],
                row["gross_revenue"]
            ),
            axis=1
        )

        output["asuransi"] = "N"

        output["KOLOM BANTU 1"] = ""
        output["KOLOM BANTU 2"] = ""
        output["KOLOM BANTU 3"] = ""

        output["nama produk 1"] = df.apply(
            lambda row: DataProcessorSPX.build_product_1(
                row["product_normalized"],
                row["product_price"],
                row["notes"],
                row["label_produk"]
            ),
            axis=1
        )

        output["nama produk 2"] = df["product_normalized"]

        output["jumlah produk"] = (
            output["nama produk 1"]
            .apply(DataProcessorSPX.extract_qty_only)
        )

        output["KOLOM BANTU 4"] = ""

        output["A"] = "Dibayar Pengirim"

        output["B"] = (
            "HUBUNGI KONSUMEN SEBELUM BARANG "
            "DIKIRIM,JANGAN DIBANTING PECAH!!!"
        )

        os.makedirs(
            os.path.dirname(output_file),
            exist_ok=True
        )

        output.to_excel(
            output_file,
            index=False
        )

        return {
            "success": True,
            "total_data": len(output),
            "output_file": output_file,
            "preview": output.head(10)
        }

    @staticmethod
    def generate_default_filename():
        tomorrow = datetime.now() + timedelta(days=1)

        formatted_date = tomorrow.strftime("%d%m%y")

        return (
            f"DB_OO_TEMBAKAN_SPX_"
            f"{formatted_date}.xlsx"
        )