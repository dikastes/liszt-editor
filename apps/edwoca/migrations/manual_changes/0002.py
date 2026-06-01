def migrate_partlabel(apps, schema_editor):
    Manifestation = apps.get_model('edwoca', 'manifestation')

    Manifestation.objects.filter(part_label = 'c').update(part_label = 'j')
    Manifestation.objects.filter(part_label = 'b').update(part_label = 'j')

def migrate_completeness(apps, schema_editor):
    Manifestation = apps.get_model('edwoca', 'manifestation')

    Manifestation.objects.filter(manifestation_form = 'EX').update(completeness = 'i')

    for m in Manifestation.objects.filter(manifestation_form = 'FR'):
        m.private_comment = m.private_comment + '\nFragment'
        m.needs_review = True
        m.save()

# operations =
        migrations.RunPython(migrate_partlabel, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(migrate_completeness, reverse_code=migrations.RunPython.noop),
