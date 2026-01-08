import csv
import io

from django import forms


class ImportRepairPlanDataForm(forms.Form):
    file = forms.FileField(label="CSVファイル")

    def clean_file(self):
        file = self.cleaned_data["file"]
        if not file.name.endswith(".csv"):
            raise forms.ValidationError("CSVファイルのみ対応")

        self._instances = []
        reader = csv.reader(io.TextIOWrapper(file, encoding="utf-8"))

        for i, row in enumerate(reader):
            # validation & instance creation
            pass

        return file

    def save(self):
        for obj in self._instances:
            obj.save()
