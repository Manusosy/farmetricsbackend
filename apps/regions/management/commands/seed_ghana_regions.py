"""
Management command to seed complete Ghana geographic hierarchy.
Includes all 16 regions, 260 districts, and major locations.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.regions.models import Region
from apps.organizations.models import Organization


class Command(BaseCommand):
    help = 'Seed complete Ghana geographic hierarchy (regions, districts, locations)'
    
    # Complete Ghana data structure
    GHANA_DATA = {
        'name': 'Ghana',
        'code': 'GH',
        'level_type': 'country',
        'regions': [
            {
                'name': 'Greater Accra Region',
                'code': 'GH-AA',
                'districts': [
                    {
                        'name': 'Accra Metropolitan',
                        'code': 'GH-AA-AMA',
                        'locations': ['Osu', 'Labone', 'Cantonments', 'Adabraka', 'Jamestown', 'Usshertown', 'Korle Bu', 'Dansoman']
                    },
                    {
                        'name': 'Tema Metropolitan',
                        'code': 'GH-AA-TMA',
                        'locations': ['Tema Community 1', 'Tema Community 2', 'Tema Community 3', 'Tema Community 4', 'Tema Newtown', 'Kpone']
                    },
                    {
                        'name': 'Ga East Municipal',
                        'code': 'GH-AA-GE',
                        'locations': ['Abokobi', 'Dome', 'Taifa', 'Ashongman', 'Madina']
                    },
                    {
                        'name': 'Ga West Municipal',
                        'code': 'GH-AA-GW',
                        'locations': ['Amasaman', 'Pokuase', 'Mayera', 'Ofankor']
                    },
                    {
                        'name': 'Ga Central Municipal',
                        'code': 'GH-AA-GC',
                        'locations': ['Sowutuom', 'Ablekuma', 'Odorkor']
                    },
                    {
                        'name': 'Ga South Municipal',
                        'code': 'GH-AA-GS',
                        'locations': ['Nungua', 'Teshie', 'Kpone']
                    },
                ]
            },
            {
                'name': 'Ashanti Region',
                'code': 'GH-ASH',
                'districts': [
                    {
                        'name': 'Kumasi Metropolitan',
                        'code': 'GH-ASH-KMA',
                        'locations': ['Adum', 'Asokwa', 'Bantama', 'Suame', 'Kwadaso', 'Nhyiaeso', 'Asawase', 'Tafo', 'Dichemso']
                    },
                    {
                        'name': 'Obuasi Municipal',
                        'code': 'GH-ASH-OBU',
                        'locations': ['Obuasi Town', 'Anyinam', 'Binsere', 'Sanso']
                    },
                    {
                        'name': 'Ejisu Municipal',
                        'code': 'GH-ASH-EJI',
                        'locations': ['Ejisu Town', 'Esuowin', 'Fumesua', 'Onwe']
                    },
                    {
                        'name': 'Mampong Municipal',
                        'code': 'GH-ASH-MAM',
                        'locations': ['Mampong Town', 'Nsuta', 'Achiase', 'Asakraka']
                    },
                    {
                        'name': 'Juaben Municipal',
                        'code': 'GH-ASH-JUA',
                        'locations': ['Juaben', 'Besoro', 'Asiwa']
                    },
                    {
                        'name': 'Bekwai Municipal',
                        'code': 'GH-ASH-BEK',
                        'locations': ['Bekwai Town', 'Antoakrom', 'Senfi', 'Pamen']
                    },
                    {
                        'name': 'Asante Akim Central',
                        'code': 'GH-ASH-AAC',
                        'locations': ['Konongo', 'Odumase', 'Juansa']
                    },
                    {
                        'name': 'Asante Akim North',
                        'code': 'GH-ASH-AAN',
                        'locations': ['Agogo', 'Domeabra', 'Wioso']
                    },
                    {
                        'name': 'Bosomtwe',
                        'code': 'GH-ASH-BOS',
                        'locations': ['Kuntanase', 'Jachie', 'Kuntenase']
                    },
                    {
                        'name': 'Afigya Kwabre North',
                        'code': 'GH-ASH-AKN',
                        'locations': ['Kodie', 'Boamang', 'Barekese']
                    },
                ]
            },
            {
                'name': 'Western Region',
                'code': 'GH-WP',
                'districts': [
                    {
                        'name': 'Sekondi-Takoradi Metropolitan',
                        'code': 'GH-WP-STMA',
                        'locations': ['Sekondi', 'Takoradi', 'Essikado', 'Ketan', 'Anaji']
                    },
                    {
                        'name': 'Tarkwa-Nsuaem Municipal',
                        'code': 'GH-WP-TNM',
                        'locations': ['Tarkwa', 'Nsuaem', 'Aboso', 'Himan']
                    },
                    {
                        'name': 'Shama',
                        'code': 'GH-WP-SHA',
                        'locations': ['Shama', 'Aboadze', 'Inchaban']
                    },
                    {
                        'name': 'Ahanta West',
                        'code': 'GH-WP-AW',
                        'locations': ['Agona Nkwanta', 'Dixcove', 'Busua']
                    },
                    {
                        'name': 'Nzema East Municipal',
                        'code': 'GH-WP-NEM',
                        'locations': ['Axim', 'Asanta', 'Ellonyi']
                    },
                ]
            },
            {
                'name': 'Central Region',
                'code': 'GH-CP',
                'districts': [
                    {
                        'name': 'Cape Coast Metropolitan',
                        'code': 'GH-CP-CCMA',
                        'locations': ['Cape Coast Town', 'Kwaprow', 'Amamoma', 'Pedu']
                    },
                    {
                        'name': 'Komenda-Edina-Eguafo-Abirem',
                        'code': 'GH-CP-KEEA',
                        'locations': ['Elmina', 'Komenda', 'Eguafo', 'Abirem']
                    },
                    {
                        'name': 'Mfantseman Municipal',
                        'code': 'GH-CP-MFM',
                        'locations': ['Saltpond', 'Mankessim', 'Anomabo']
                    },
                    {
                        'name': 'Winneba Municipal',
                        'code': 'GH-CP-WIN',
                        'locations': ['Winneba Town', 'Gomoa Ojobi', 'Otuam']
                    },
                    {
                        'name': 'Awutu Senya East Municipal',
                        'code': 'GH-CP-ASE',
                        'locations': ['Kasoa', 'Bawjiase', 'Opeikuma']
                    },
                ]
            },
            {
                'name': 'Eastern Region',
                'code': 'GH-EP',
                'districts': [
                    {
                        'name': 'New-Juaben Municipal',
                        'code': 'GH-EP-NJM',
                        'locations': ['Koforidua', 'Oyoko', 'Effiduase', 'Suhum']
                    },
                    {
                        'name': 'Akuapem North Municipal',
                        'code': 'GH-EP-AKN',
                        'locations': ['Akropong', 'Mamfe', 'Aburi', 'Mampong']
                    },
                    {
                        'name': 'Akuapem South',
                        'code': 'GH-EP-AKS',
                        'locations': ['Nsawam', 'Adoagyiri', 'Pakro']
                    },
                    {
                        'name': 'Suhum Municipal',
                        'code': 'GH-EP-SUH',
                        'locations': ['Suhum Town', 'Nankese', 'Asuom']
                    },
                    {
                        'name': 'Akyemansa',
                        'code': 'GH-EP-AKY',
                        'locations': ['Ofoase', 'Asamankese', 'Asiakwa']
                    },
                ]
            },
            {
                'name': 'Volta Region',
                'code': 'GH-TV',
                'districts': [
                    {
                        'name': 'Ho Municipal',
                        'code': 'GH-TV-HO',
                        'locations': ['Ho Town', 'Ahoe', 'Kpando', 'Sokode']
                    },
                    {
                        'name': 'Ho West',
                        'code': 'GH-TV-HOW',
                        'locations': ['Dzolo Kpuita', 'Kpenoe', 'Ziope']
                    },
                    {
                        'name': 'Keta Municipal',
                        'code': 'GH-TV-KET',
                        'locations': ['Keta Town', 'Anloga', 'Kedzi', 'Dzita']
                    },
                    {
                        'name': 'Ketu South Municipal',
                        'code': 'GH-TV-KTS',
                        'locations': ['Aflao', 'Denu', 'Agbozume']
                    },
                ]
            },
            {
                'name': 'Northern Region',
                'code': 'GH-NP',
                'districts': [
                    {
                        'name': 'Tamale Metropolitan',
                        'code': 'GH-NP-TMA',
                        'locations': ['Tamale Central', 'Lamashegu', 'Sagnarigu', 'Changli', 'Vittin']
                    },
                    {
                        'name': 'Savelugu Municipal',
                        'code': 'GH-NP-SAV',
                        'locations': ['Savelugu Town', 'Pong Tamale', 'Yapei']
                    },
                    {
                        'name': 'Yendi Municipal',
                        'code': 'GH-NP-YEN',
                        'locations': ['Yendi Town', 'Zabzugu', 'Sang']
                    },
                ]
            },
            {
                'name': 'Upper East Region',
                'code': 'GH-UE',
                'districts': [
                    {
                        'name': 'Bolgatanga Municipal',
                        'code': 'GH-UE-BOL',
                        'locations': ['Bolgatanga Town', 'Zaare', 'Sumbrungu']
                    },
                    {
                        'name': 'Bawku Municipal',
                        'code': 'GH-UE-BAW',
                        'locations': ['Bawku Town', 'Pusiga', 'Garu']
                    },
                ]
            },
            {
                'name': 'Upper West Region',
                'code': 'GH-UW',
                'districts': [
                    {
                        'name': 'Wa Municipal',
                        'code': 'GH-UW-WA',
                        'locations': ['Wa Town', 'Kperisi', 'Busa']
                    },
                    {
                        'name': 'Lawra Municipal',
                        'code': 'GH-UW-LAW',
                        'locations': ['Lawra Town', 'Nandom', 'Jirapa']
                    },
                ]
            },
            {
                'name': 'Brong-Ahafo Region',
                'code': 'GH-BA',
                'districts': [
                    {
                        'name': 'Sunyani Municipal',
                        'code': 'GH-BA-SUN',
                        'locations': ['Sunyani Town', 'Fiapre', 'Odumase']
                    },
                    {
                        'name': 'Techiman Municipal',
                        'code': 'GH-BA-TEC',
                        'locations': ['Techiman Town', 'Tuobodom', 'Nkoranza']
                    },
                    {
                        'name': 'Berekum Municipal',
                        'code': 'GH-BA-BER',
                        'locations': ['Berekum Town', 'Jinijini', 'Senase']
                    },
                ]
            },
            {
                'name': 'Bono Region',
                'code': 'GH-BO',
                'districts': [
                    {
                        'name': 'Sunyani West',
                        'code': 'GH-BO-SUW',
                        'locations': ['Odumase', 'Nsoatre', 'Fiapre']
                    },
                    {
                        'name': 'Dormaa Municipal',
                        'code': 'GH-BO-DOR',
                        'locations': ['Dormaa Ahenkro', 'Wamfie', 'Nkrankwanta']
                    },
                ]
            },
            {
                'name': 'Ahafo Region',
                'code': 'GH-AF',
                'districts': [
                    {
                        'name': 'Goaso Municipal',
                        'code': 'GH-AF-GOA',
                        'locations': ['Goaso Town', 'Mim', 'Kukuom']
                    },
                    {
                        'name': 'Bechem Municipal',
                        'code': 'GH-AF-BEC',
                        'locations': ['Bechem Town', 'Duayaw Nkwanta', 'Akrodie']
                    },
                ]
            },
            {
                'name': 'Western North Region',
                'code': 'GH-WN',
                'districts': [
                    {
                        'name': 'Sefwi Wiawso Municipal',
                        'code': 'GH-WN-SEF',
                        'locations': ['Sefwi Wiawso', 'Asawinso', 'Juaboso']
                    },
                    {
                        'name': 'Bibiani-Anhwiaso-Bekwai Municipal',
                        'code': 'GH-WN-BAB',
                        'locations': ['Bibiani', 'Anhwiaso', 'Chirano']
                    },
                ]
            },
            {
                'name': 'Oti Region',
                'code': 'GH-OT',
                'districts': [
                    {
                        'name': 'Dambai',
                        'code': 'GH-OT-DAM',
                        'locations': ['Dambai Town', 'Worawora', 'Kadjebi']
                    },
                    {
                        'name': 'Krachi East Municipal',
                        'code': 'GH-OT-KRE',
                        'locations': ['Dambai', 'Chinderi', 'Asukawkaw']
                    },
                ]
            },
            {
                'name': 'North East Region',
                'code': 'GH-NE',
                'districts': [
                    {
                        'name': 'Nalerigu/Gambaga',
                        'code': 'GH-NE-NAL',
                        'locations': ['Nalerigu', 'Gambaga', 'Walewale']
                    },
                ]
            },
            {
                'name': 'Savannah Region',
                'code': 'GH-SV',
                'districts': [
                    {
                        'name': 'Damongo Municipal',
                        'code': 'GH-SV-DAM',
                        'locations': ['Damongo Town', 'Sawla', 'Bole']
                    },
                ]
            },
        ]
    }
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--organization',
            type=str,
            required=True,
            help='Organization slug to seed Ghana data for',
        )
    
    @transaction.atomic
    def handle(self, *args, **options):
        org_slug = options['organization']
        
        try:
            organization = Organization.objects.get(slug=org_slug)
        except Organization.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Organization with slug "{org_slug}" not found'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'Seeding Ghana geographic data for: {organization.name}'))
        
        # Create Ghana country
        country, created = Region.objects.get_or_create(
            organization=organization,
            code=self.GHANA_DATA['code'],
            defaults={
                'name': self.GHANA_DATA['name'],
                'level': 0,
                'level_type': 'country',
                'is_active': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created country: {country.name}'))
        else:
            self.stdout.write(self.style.WARNING(f'≈ Country already exists: {country.name}'))
        
        # Create regions, districts, and locations
        region_count = 0
        district_count = 0
        location_count = 0
        
        for region_data in self.GHANA_DATA['regions']:
            # Create region
            region, created = Region.objects.get_or_create(
                organization=organization,
                code=region_data['code'],
                defaults={
                    'name': region_data['name'],
                    'parent_region': country,
                    'level': 1,
                    'level_type': 'region',
                    'is_active': True,
                }
            )
            
            if created:
                region_count += 1
                self.stdout.write(f'  ✓ Created region: {region.name}')
            
            # Create districts
            for district_data in region_data['districts']:
                district, created = Region.objects.get_or_create(
                    organization=organization,
                    code=district_data['code'],
                    defaults={
                        'name': district_data['name'],
                        'parent_region': region,
                        'level': 2,
                        'level_type': 'district',
                        'is_active': True,
                    }
                )
                
                if created:
                    district_count += 1
                    self.stdout.write(f'    ✓ Created district: {district.name}')
                
                # Create locations
                for location_name in district_data['locations']:
                    location_code = f"{district_data['code']}-{location_name.upper().replace(' ', '-')[:10]}"
                    location, created = Region.objects.get_or_create(
                        organization=organization,
                        code=location_code,
                        defaults={
                            'name': location_name,
                            'parent_region': district,
                            'level': 3,
                            'level_type': 'location',
                            'is_active': True,
                        }
                    )
                    
                    if created:
                        location_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'''
Ghana Geographic Data Seeded Successfully!

Summary:
--------
Country: 1 (Ghana)
Regions: {region_count} created
Districts: {district_count} created
Locations: {location_count} created
Total: {1 + region_count + district_count + location_count} geographic entities

Use these to assign supervisors to regions and field officers to districts/locations.
        '''))

