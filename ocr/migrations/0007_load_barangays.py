from django.db import migrations

def create_barangays(apps, schema_editor):
    Barangay = apps.get_model('ocr', 'Barangay')
    names = [
        "Amsipit", "Bales", "Colon", "Daliao", "Kabatiol", "Kablacan",
        "Kamanga", "Kanalo", "Lumasal", "Lumatil", "Malbang", "Nomoh",
        "Pananag", "Poblacion", "Seven Hills", "Tinoto",
    ]
    for n in names:
        Barangay.objects.create(name=n)

class Migration(migrations.Migration):
    dependencies = [
        ('ocr', '0001_initial'),  # adjust if your initial migration is named differently
    ]
    operations = [
        migrations.RunPython(create_barangays),
    ]
