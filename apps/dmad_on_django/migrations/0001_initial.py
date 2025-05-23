# Generated by Django 5.1.4 on 2025-04-15 13:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Period',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('not_before', models.DateField(blank=True, null=True)),
                ('not_after', models.DateField(blank=True, null=True)),
                ('display', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('raw_data', models.TextField(null=True)),
                ('rework_in_gnd', models.BooleanField(default=False)),
                ('gnd_id', models.CharField(blank=True, max_length=20, null=True)),
                ('gender', models.CharField(choices=[('m', 'male'), ('f', 'female'), ('', 'null')], default='', max_length=1, null=True)),
                ('geographic_area_code', models.CharField(max_length=10, null=True)),
                ('description', models.TextField(null=True)),
                ('birth_date', models.DateField(blank=True, null=True)),
                ('death_date', models.DateField(blank=True, null=True)),
                ('comment', models.TextField(blank=True, null=True)),
                ('interim_designator', models.CharField(blank=True, max_length=150, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Work',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='PersonName',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=20)),
                ('last_name', models.CharField(max_length=20)),
                ('language', models.CharField(choices=[('DE', 'German'), ('FR', 'French'), ('HU', 'Hungarian'), ('EN', 'English'), ('AA', 'Afar'), ('AB', 'Abkhazian; Abkhaz'), ('', 'Zaza; Dimili; Dimli; Kirdki; Kirmanjki; Zazaki'), ('AF', 'Afrikaans'), ('AK', 'Akan'), ('SQ', 'Albanian'), ('AM', 'Amharic'), ('AR', 'Arabic'), ('AN', 'Aragonese'), ('HY', 'Armenian'), ('AS', 'Assamese'), ('AV', 'Avaric'), ('AE', 'Avestan'), ('AY', 'Aymara'), ('AZ', 'Azerbaijani'), ('BA', 'Bashkir'), ('BM', 'Bambara'), ('EU', 'Basque'), ('BE', 'Belarusian'), ('BN', 'Bengali; Bangla'), ('BH', 'Bihari languages; Bihari'), ('BI', 'Bislama'), ('BS', 'Bosnian'), ('BR', 'Breton'), ('BG', 'Bulgarian'), ('MY', 'Burmese'), ('CA', 'Catalan; Valencian'), ('CH', 'Chamorro'), ('CE', 'Chechen'), ('ZH', 'Chinese'), ('CU', 'Church Slavic; Old Slavonic; Church Slavonic; Old Bulgarian; Old Church Slavonic'), ('CV', 'Chuvash'), ('KW', 'Cornish'), ('CO', 'Corsican'), ('CR', 'Cree'), ('CS', 'Czech'), ('DA', 'Danish'), ('DV', 'Divehi; Dhivehi; Maldivian'), ('NL', 'Dutch; Flemish'), ('DZ', 'Dzongkha'), ('EO', 'Esperanto'), ('ET', 'Estonian'), ('EE', 'Ewe'), ('FO', 'Faroese'), ('FJ', 'Fijian'), ('FI', 'Finnish'), ('FY', 'Western Frisian'), ('FF', 'Fulah; Fula; Pulaar; Pular'), ('KA', 'Georgian'), ('GD', 'Gaelic; Scottish Gaelic'), ('GA', 'Irish'), ('GL', 'Galician'), ('GV', 'Manx'), ('EL', 'Greek, Modern (1453-); Greek'), ('GN', 'Guarani; Guaraní'), ('GU', 'Gujarati'), ('HT', 'Haitian; Haitian Creole'), ('HA', 'Hausa'), ('HE', 'Hebrew'), ('HZ', 'Herero'), ('HI', 'Hindi'), ('HO', 'Hiri Motu'), ('HR', 'Croatian'), ('IG', 'Igbo'), ('IS', 'Icelandic'), ('IO', 'Ido'), ('II', 'Sichuan Yi; Nuosu'), ('IU', 'Inuktitut'), ('IE', 'Interlingue; Occidental'), ('IA', 'Interlingua (International Auxiliary Language Association)'), ('ID', 'Indonesian'), ('IK', 'Inupiaq'), ('IT', 'Italian'), ('JV', 'Javanese'), ('JA', 'Japanese'), ('KL', 'Kalaallisut; Greenlandic'), ('KN', 'Kannada'), ('KS', 'Kashmiri'), ('KR', 'Kanuri'), ('KK', 'Kazakh'), ('KM', 'Central Khmer; Khmer'), ('KI', 'Kikuyu; Gikuyu'), ('RW', 'Kinyarwanda'), ('KY', 'Kirghiz; Kyrgyz'), ('KV', 'Komi'), ('KG', 'Kongo'), ('KO', 'Korean'), ('KJ', 'Kuanyama; Kwanyama'), ('KU', 'Kurdish'), ('LO', 'Lao'), ('LA', 'Latin'), ('LV', 'Latvian'), ('LI', 'Limburgan; Limburger; Limburgish'), ('LN', 'Lingala'), ('LT', 'Lithuanian'), ('LB', 'Luxembourgish; Letzeburgesch'), ('LU', 'Luba-Katanga'), ('LG', 'Ganda'), ('MK', 'Macedonian'), ('MH', 'Marshallese'), ('ML', 'Malayalam'), ('MI', 'Maori; Māori'), ('MR', 'Marathi; Marāṭhī'), ('MS', 'Malay'), ('MG', 'Malagasy'), ('MT', 'Maltese'), ('MN', 'Mongolian'), ('NA', 'Nauru; Nauruan'), ('NV', 'Navajo; Navaho'), ('NR', 'Ndebele, South; South Ndebele; Southern Ndebele'), ('ND', 'Ndebele, North; North Ndebele; Northern Ndebele'), ('NG', 'Ndonga'), ('NE', 'Nepali'), ('NN', 'Norwegian Nynorsk; Nynorsk, Norwegian'), ('NB', 'Bokmål, Norwegian; Norwegian Bokmål'), ('NO', 'Norwegian'), ('NY', 'Chichewa; Chewa; Nyanja'), ('OC', 'Occitan (post 1500); Provençal'), ('OJ', 'Ojibwa; Ojibwe'), ('OR', 'Oriya'), ('OM', 'Oromo'), ('OS', 'Ossetian; Ossetic'), ('PA', 'Panjabi; Punjabi'), ('FA', 'Persian; Farsi'), ('PI', 'Pali; Pāli'), ('PL', 'Polish'), ('PT', 'Portuguese'), ('PS', 'Pushto; Pashto'), ('QU', 'Quechua'), ('RC', 'Reunionese;Reunion Creole'), ('RM', 'Romansh'), ('RO', 'Romanian; Moldavian; Moldovan'), ('RN', 'Rundi; Kirundi'), ('RU', 'Russian'), ('SG', 'Sango'), ('SA', 'Sanskrit; Saṁskṛta'), ('SI', 'Sinhala; Sinhalese'), ('SK', 'Slovak'), ('SL', 'Slovenian; Slovene'), ('SE', 'Northern Sami'), ('SM', 'Samoan'), ('SN', 'Shona'), ('SD', 'Sindhi'), ('SO', 'Somali'), ('ST', 'Sotho, Southern; Southern Sotho'), ('ES', 'Spanish; Castilian'), ('SC', 'Sardinian'), ('SR', 'Serbian'), ('SS', 'Swati'), ('SU', 'Sundanese'), ('SW', 'Swahili'), ('SV', 'Swedish'), ('TY', 'Tahitian'), ('TA', 'Tamil'), ('TT', 'Tatar'), ('TE', 'Telugu'), ('TG', 'Tajik'), ('TL', 'Tagalog'), ('TH', 'Thai'), ('BO', 'Tibetan; Tibetan Standard; Central'), ('TI', 'Tigrinya'), ('TO', 'Tonga (Tonga Islands)'), ('TN', 'Tswana'), ('TS', 'Tsonga'), ('TK', 'Turkmen'), ('TR', 'Turkish'), ('TW', 'Twi'), ('UG', 'Uighur; Uyghur'), ('UK', 'Ukrainian'), ('UR', 'Urdu'), ('UZ', 'Uzbek'), ('VE', 'Venda'), ('VI', 'Vietnamese'), ('VO', 'Volapük'), ('CY', 'Welsh'), ('WA', 'Walloon'), ('WO', 'Wolof'), ('XH', 'Xhosa'), ('YI', 'Yiddish'), ('YO', 'Yoruba'), ('ZA', 'Zhuang; Chuang'), ('ZU', 'Zulu')], default='German', max_length=15, null=True)),
                ('status', models.CharField(choices=[('P', 'Primary'), ('A', 'Alternative')], default='P', max_length=1, null=True)),
                ('person', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='names', to='dmad.person')),
            ],
        ),
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gnd_id', models.CharField(max_length=20)),
                ('long', models.DecimalField(decimal_places=6, default=0, max_digits=9, null=True)),
                ('lat', models.DecimalField(decimal_places=6, default=0, max_digits=9, null=True)),
                ('description', models.TextField(null=True)),
                ('raw_data', models.TextField(null=True)),
                ('parent_place', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='child_places', to='dmad.place')),
            ],
        ),
        migrations.AddField(
            model_name='person',
            name='activity_places',
            field=models.ManyToManyField(to='dmad.place'),
        ),
        migrations.AddField(
            model_name='person',
            name='birth_place',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='birth_place_of', to='dmad.place'),
        ),
        migrations.AddField(
            model_name='person',
            name='death_place',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='death_place_of', to='dmad.place'),
        ),
        migrations.CreateModel(
            name='PlaceName',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, null=True)),
                ('language', models.CharField(choices=[('DE', 'German'), ('FR', 'French'), ('HU', 'Hungarian'), ('EN', 'English'), ('AA', 'Afar'), ('AB', 'Abkhazian; Abkhaz'), ('', 'Zaza; Dimili; Dimli; Kirdki; Kirmanjki; Zazaki'), ('AF', 'Afrikaans'), ('AK', 'Akan'), ('SQ', 'Albanian'), ('AM', 'Amharic'), ('AR', 'Arabic'), ('AN', 'Aragonese'), ('HY', 'Armenian'), ('AS', 'Assamese'), ('AV', 'Avaric'), ('AE', 'Avestan'), ('AY', 'Aymara'), ('AZ', 'Azerbaijani'), ('BA', 'Bashkir'), ('BM', 'Bambara'), ('EU', 'Basque'), ('BE', 'Belarusian'), ('BN', 'Bengali; Bangla'), ('BH', 'Bihari languages; Bihari'), ('BI', 'Bislama'), ('BS', 'Bosnian'), ('BR', 'Breton'), ('BG', 'Bulgarian'), ('MY', 'Burmese'), ('CA', 'Catalan; Valencian'), ('CH', 'Chamorro'), ('CE', 'Chechen'), ('ZH', 'Chinese'), ('CU', 'Church Slavic; Old Slavonic; Church Slavonic; Old Bulgarian; Old Church Slavonic'), ('CV', 'Chuvash'), ('KW', 'Cornish'), ('CO', 'Corsican'), ('CR', 'Cree'), ('CS', 'Czech'), ('DA', 'Danish'), ('DV', 'Divehi; Dhivehi; Maldivian'), ('NL', 'Dutch; Flemish'), ('DZ', 'Dzongkha'), ('EO', 'Esperanto'), ('ET', 'Estonian'), ('EE', 'Ewe'), ('FO', 'Faroese'), ('FJ', 'Fijian'), ('FI', 'Finnish'), ('FY', 'Western Frisian'), ('FF', 'Fulah; Fula; Pulaar; Pular'), ('KA', 'Georgian'), ('GD', 'Gaelic; Scottish Gaelic'), ('GA', 'Irish'), ('GL', 'Galician'), ('GV', 'Manx'), ('EL', 'Greek, Modern (1453-); Greek'), ('GN', 'Guarani; Guaraní'), ('GU', 'Gujarati'), ('HT', 'Haitian; Haitian Creole'), ('HA', 'Hausa'), ('HE', 'Hebrew'), ('HZ', 'Herero'), ('HI', 'Hindi'), ('HO', 'Hiri Motu'), ('HR', 'Croatian'), ('IG', 'Igbo'), ('IS', 'Icelandic'), ('IO', 'Ido'), ('II', 'Sichuan Yi; Nuosu'), ('IU', 'Inuktitut'), ('IE', 'Interlingue; Occidental'), ('IA', 'Interlingua (International Auxiliary Language Association)'), ('ID', 'Indonesian'), ('IK', 'Inupiaq'), ('IT', 'Italian'), ('JV', 'Javanese'), ('JA', 'Japanese'), ('KL', 'Kalaallisut; Greenlandic'), ('KN', 'Kannada'), ('KS', 'Kashmiri'), ('KR', 'Kanuri'), ('KK', 'Kazakh'), ('KM', 'Central Khmer; Khmer'), ('KI', 'Kikuyu; Gikuyu'), ('RW', 'Kinyarwanda'), ('KY', 'Kirghiz; Kyrgyz'), ('KV', 'Komi'), ('KG', 'Kongo'), ('KO', 'Korean'), ('KJ', 'Kuanyama; Kwanyama'), ('KU', 'Kurdish'), ('LO', 'Lao'), ('LA', 'Latin'), ('LV', 'Latvian'), ('LI', 'Limburgan; Limburger; Limburgish'), ('LN', 'Lingala'), ('LT', 'Lithuanian'), ('LB', 'Luxembourgish; Letzeburgesch'), ('LU', 'Luba-Katanga'), ('LG', 'Ganda'), ('MK', 'Macedonian'), ('MH', 'Marshallese'), ('ML', 'Malayalam'), ('MI', 'Maori; Māori'), ('MR', 'Marathi; Marāṭhī'), ('MS', 'Malay'), ('MG', 'Malagasy'), ('MT', 'Maltese'), ('MN', 'Mongolian'), ('NA', 'Nauru; Nauruan'), ('NV', 'Navajo; Navaho'), ('NR', 'Ndebele, South; South Ndebele; Southern Ndebele'), ('ND', 'Ndebele, North; North Ndebele; Northern Ndebele'), ('NG', 'Ndonga'), ('NE', 'Nepali'), ('NN', 'Norwegian Nynorsk; Nynorsk, Norwegian'), ('NB', 'Bokmål, Norwegian; Norwegian Bokmål'), ('NO', 'Norwegian'), ('NY', 'Chichewa; Chewa; Nyanja'), ('OC', 'Occitan (post 1500); Provençal'), ('OJ', 'Ojibwa; Ojibwe'), ('OR', 'Oriya'), ('OM', 'Oromo'), ('OS', 'Ossetian; Ossetic'), ('PA', 'Panjabi; Punjabi'), ('FA', 'Persian; Farsi'), ('PI', 'Pali; Pāli'), ('PL', 'Polish'), ('PT', 'Portuguese'), ('PS', 'Pushto; Pashto'), ('QU', 'Quechua'), ('RC', 'Reunionese;Reunion Creole'), ('RM', 'Romansh'), ('RO', 'Romanian; Moldavian; Moldovan'), ('RN', 'Rundi; Kirundi'), ('RU', 'Russian'), ('SG', 'Sango'), ('SA', 'Sanskrit; Saṁskṛta'), ('SI', 'Sinhala; Sinhalese'), ('SK', 'Slovak'), ('SL', 'Slovenian; Slovene'), ('SE', 'Northern Sami'), ('SM', 'Samoan'), ('SN', 'Shona'), ('SD', 'Sindhi'), ('SO', 'Somali'), ('ST', 'Sotho, Southern; Southern Sotho'), ('ES', 'Spanish; Castilian'), ('SC', 'Sardinian'), ('SR', 'Serbian'), ('SS', 'Swati'), ('SU', 'Sundanese'), ('SW', 'Swahili'), ('SV', 'Swedish'), ('TY', 'Tahitian'), ('TA', 'Tamil'), ('TT', 'Tatar'), ('TE', 'Telugu'), ('TG', 'Tajik'), ('TL', 'Tagalog'), ('TH', 'Thai'), ('BO', 'Tibetan; Tibetan Standard; Central'), ('TI', 'Tigrinya'), ('TO', 'Tonga (Tonga Islands)'), ('TN', 'Tswana'), ('TS', 'Tsonga'), ('TK', 'Turkmen'), ('TR', 'Turkish'), ('TW', 'Twi'), ('UG', 'Uighur; Uyghur'), ('UK', 'Ukrainian'), ('UR', 'Urdu'), ('UZ', 'Uzbek'), ('VE', 'Venda'), ('VI', 'Vietnamese'), ('VO', 'Volapük'), ('CY', 'Welsh'), ('WA', 'Walloon'), ('WO', 'Wolof'), ('XH', 'Xhosa'), ('YI', 'Yiddish'), ('YO', 'Yoruba'), ('ZA', 'Zhuang; Chuang'), ('ZU', 'Zulu')], default='German', max_length=15, null=True)),
                ('status', models.CharField(choices=[('P', 'Primary'), ('A', 'Alternative')], default='P', max_length=1, null=True)),
                ('place', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='names', to='dmad.place')),
            ],
        ),
    ]
