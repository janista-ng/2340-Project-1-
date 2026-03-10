import csv
from django.http import HttpResponse


def export_as_csv(modeladmin, request, queryset):
    meta = modeladmin.model._meta
    field_names = [field.name for field in meta.fields]

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{meta.model_name}_export.csv"'

    writer = csv.writer(response)
    writer.writerow(field_names)

    for obj in queryset:
        row = []
        for field_name in field_names:
            value = getattr(obj, field_name)

            if hasattr(value, "pk"):
                row.append(str(value))
            else:
                row.append(value)

        writer.writerow(row)

    return response


export_as_csv.short_description = "Export selected rows to CSV"