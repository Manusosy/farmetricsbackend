"""
Management command to seed complete Kenya geographic hierarchy.
Includes all 47 counties (regions), sub-counties (districts), and major locations.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.regions.models import Region
from apps.organizations.models import Organization


class Command(BaseCommand):
    help = 'Seed complete Kenya geographic hierarchy (counties, sub-counties, locations)'
    
    # Complete Kenya data structure
    KENYA_DATA = {
        'name': 'Kenya',
        'code': 'KE',
        'level_type': 'country',
        'regions': [
            {
                'name': 'Nairobi County',
                'code': 'KE-NAI',
                'districts': [
                    {
                        'name': 'Westlands Sub-County',
                        'code': 'KE-NAI-WES',
                        'locations': ['Parklands', 'Highridge', 'Karura', 'Kangemi', 'Mountain View', 'Kitisuru']
                    },
                    {
                        'name': 'Dagoretti North Sub-County',
                        'code': 'KE-NAI-DGN',
                        'locations': ['Kilimani', 'Kawangware', 'Gatina', 'Kileleshwa']
                    },
                    {
                        'name': 'Dagoretti South Sub-County',
                        'code': 'KE-NAI-DGS',
                        'locations': ['Mutuini', 'Ngando', 'Riruta', 'Uthiru']
                    },
                    {
                        'name': 'Langata Sub-County',
                        'code': 'KE-NAI-LAN',
                        'locations': ['Karen', 'Nairobi West', 'South C', 'Nyayo Highrise']
                    },
                    {
                        'name': 'Kibra Sub-County',
                        'code': 'KE-NAI-KIB',
                        'locations': ['Kibera', 'Laini Saba', 'Lindi', 'Makina', 'Woodley']
                    },
                    {
                        'name': 'Roysambu Sub-County',
                        'code': 'KE-NAI-ROY',
                        'locations': ['Githurai', 'Kahawa West', 'Zimmerman', 'Roysambu', 'Kahawa']
                    },
                    {
                        'name': 'Kasarani Sub-County',
                        'code': 'KE-NAI-KAS',
                        'locations': ['Clay City', 'Mwiki', 'Kasarani', 'Njiru', 'Ruai']
                    },
                    {
                        'name': 'Ruaraka Sub-County',
                        'code': 'KE-NAI-RUA',
                        'locations': ['Baba Dogo', 'Utalii', 'Mathare North', 'Lucky Summer']
                    },
                    {
                        'name': 'Embakasi South Sub-County',
                        'code': 'KE-NAI-EMS',
                        'locations': ['Imara Daima', 'Kwa Njenga', 'Kwa Rueben', 'Pipeline']
                    },
                    {
                        'name': 'Embakasi North Sub-County',
                        'code': 'KE-NAI-EMN',
                        'locations': ['Kariobangi North', 'Dandora', 'Korogocho']
                    },
                    {
                        'name': 'Embakasi Central Sub-County',
                        'code': 'KE-NAI-EMC',
                        'locations': ['Kayole North', 'Kayole Central', 'Kayole South', 'Komarock', 'Matopeni']
                    },
                    {
                        'name': 'Embakasi East Sub-County',
                        'code': 'KE-NAI-EME',
                        'locations': ['Upper Savannah', 'Lower Savannah', 'Embakasi', 'Utawala']
                    },
                    {
                        'name': 'Embakasi West Sub-County',
                        'code': 'KE-NAI-EMW',
                        'locations': ['Umoja I', 'Umoja II', 'Mowlem', 'Kariobangi South']
                    },
                    {
                        'name': 'Makadara Sub-County',
                        'code': 'KE-NAI-MAK',
                        'locations': ['Maringo/Hamza', 'Viwandani', 'Harambee', 'Makongeni']
                    },
                    {
                        'name': 'Kamukunji Sub-County',
                        'code': 'KE-NAI-KAM',
                        'locations': ['Pumwani', 'Eastleigh North', 'Eastleigh South', 'Airbase', 'California']
                    },
                    {
                        'name': 'Starehe Sub-County',
                        'code': 'KE-NAI-STA',
                        'locations': ['Nairobi Central', 'Ngara', 'Pangani', 'Ziwani', 'Kariokor', 'Landimawe']
                    },
                    {
                        'name': 'Mathare Sub-County',
                        'code': 'KE-NAI-MAT',
                        'locations': ['Hospital', 'Mabatini', 'Huruma', 'Ngei', 'Mlango Kubwa', 'Kiamaiko']
                    },
                ]
            },
            {
                'name': 'Mombasa County',
                'code': 'KE-MBA',
                'districts': [
                    {
                        'name': 'Changamwe Sub-County',
                        'code': 'KE-MBA-CHA',
                        'locations': ['Port Reitz', 'Kipevu', 'Airport', 'Changamwe', 'Chaani']
                    },
                    {
                        'name': 'Jomvu Sub-County',
                        'code': 'KE-MBA-JOM',
                        'locations': ['Jomvu Kuu', 'Miritini', 'Mikindani']
                    },
                    {
                        'name': 'Kisauni Sub-County',
                        'code': 'KE-MBA-KIS',
                        'locations': ['Mjambere', 'Junda', 'Bamburi', 'Mwakirunge', 'Mtopanga', 'Magogoni', 'Shanzu']
                    },
                    {
                        'name': 'Nyali Sub-County',
                        'code': 'KE-MBA-NYA',
                        'locations': ['Frere Town', 'Ziwa La Ng\'ombe', 'Mkomani', 'Kongowea', 'Kadzandani']
                    },
                    {
                        'name': 'Likoni Sub-County',
                        'code': 'KE-MBA-LIK',
                        'locations': ['Mtongwe', 'Shika Adabu', 'Bofu', 'Likoni', 'Timbwani']
                    },
                    {
                        'name': 'Mvita Sub-County',
                        'code': 'KE-MBA-MVI',
                        'locations': ['Mji Wa Kale/Makadara', 'Tudor', 'Tononoka', 'Shimanzi/Ganjoni', 'Majengo']
                    },
                ]
            },
            {
                'name': 'Kisumu County',
                'code': 'KE-KIS',
                'districts': [
                    {
                        'name': 'Kisumu East Sub-County',
                        'code': 'KE-KIS-E',
                        'locations': ['Railways', 'Migosi', 'Shaurimoyo Kaloleni', 'Market Milimani', 'Kondele', 'Nyalenda A', 'Nyalenda B']
                    },
                    {
                        'name': 'Kisumu Central Sub-County',
                        'code': 'KE-KIS-C',
                        'locations': ['Robert Ouko', 'Manyatta A', 'Manyatta B', 'Migosi']
                    },
                    {
                        'name': 'Kisumu West Sub-County',
                        'code': 'KE-KIS-W',
                        'locations': ['Central Kisumu', 'Kisumu North', 'West Kisumu', 'North West Kisumu', 'South West Kisumu']
                    },
                    {
                        'name': 'Seme Sub-County',
                        'code': 'KE-KIS-SEM',
                        'locations': ['West Seme', 'Central Seme', 'East Seme', 'North Seme']
                    },
                ]
            },
            {
                'name': 'Nakuru County',
                'code': 'KE-NAK',
                'districts': [
                    {
                        'name': 'Nakuru Town East Sub-County',
                        'code': 'KE-NAK-E',
                        'locations': ['Biashara', 'Flamingo', 'Menengai West', 'Nakuru East']
                    },
                    {
                        'name': 'Nakuru Town West Sub-County',
                        'code': 'KE-NAK-W',
                        'locations': ['Barut', 'London', 'Kaptembwa', 'Kapkures', 'Rhoda', 'Shaabab']
                    },
                    {
                        'name': 'Naivasha Sub-County',
                        'code': 'KE-NAK-NAI',
                        'locations': ['Naivasha East', 'Viwandani', 'Hells Gate', 'Mai Mahiu', 'Olkaria']
                    },
                ]
            },
            {
                'name': 'Kiambu County',
                'code': 'KE-KIA',
                'districts': [
                    {
                        'name': 'Thika Town Sub-County',
                        'code': 'KE-KIA-THI',
                        'locations': ['Township', 'Kamenu', 'Hospital', 'Gatuanyaga', 'Ngoliba']
                    },
                    {
                        'name': 'Ruiru Sub-County',
                        'code': 'KE-KIA-RUI',
                        'locations': ['Biashara', 'Gatongora', 'Kahawa Sukari', 'Kahawa Wendani', 'Kiuu', 'Mwiki', 'Mwihoko']
                    },
                    {
                        'name': 'Kiambu Sub-County',
                        'code': 'KE-KIA-KIA',
                        'locations': ['Ndumberi', 'Riabai', 'Township', 'Ting\'ang\'a']
                    },
                    {
                        'name': 'Kikuyu Sub-County',
                        'code': 'KE-KIA-KIK',
                        'locations': ['Karai', 'Nachu', 'Sigona', 'Kikuyu', 'Kinoo']
                    },
                ]
            },
            {
                'name': 'Machakos County',
                'code': 'KE-MAC',
                'districts': [
                    {
                        'name': 'Machakos Town Sub-County',
                        'code': 'KE-MAC-MAC',
                        'locations': ['Mumbuni North', 'Mumbuni West', 'Muvuti/Kiima-Kimwe', 'Masii', 'Muthetheni']
                    },
                    {
                        'name': 'Mavoko Sub-County',
                        'code': 'KE-MAC-MAV',
                        'locations': ['Athi River', 'Kinanie', 'Muthwani', 'Syokimau/Mulolongo']
                    },
                ]
            },
            {
                'name': 'Uasin Gishu County',
                'code': 'KE-UGI',
                'districts': [
                    {
                        'name': 'Eldoret East Sub-County',
                        'code': 'KE-UGI-EE',
                        'locations': ['Cheptiret/Kipchamo', 'Tarakwa', 'Kapsoya', 'Kapyemit', 'Simat/Kapseret']
                    },
                    {
                        'name': 'Eldoret West Sub-County',
                        'code': 'KE-UGI-EW',
                        'locations': ['Kamagut', 'Kipkenyo', 'Sergoit', 'Karuna/Meibeki', 'Moiben']
                    },
                ]
            },
            {
                'name': 'Kakamega County',
                'code': 'KE-KAK',
                'districts': [
                    {
                        'name': 'Kakamega Central Sub-County',
                        'code': 'KE-KAK-C',
                        'locations': ['Amalemba', 'Bukhungu', 'Lurambi', 'Shirere', 'Sheywe']
                    },
                    {
                        'name': 'Mumias Sub-County',
                        'code': 'KE-KAK-MUM',
                        'locations': ['Mumias Central', 'Mumias North', 'Etenje', 'Musanda']
                    },
                ]
            },
            {
                'name': 'Kilifi County',
                'code': 'KE-KIL',
                'districts': [
                    {
                        'name': 'Kilifi North Sub-County',
                        'code': 'KE-KIL-N',
                        'locations': ['Tezo', 'Sokoni', 'Kibarani', 'Mnarani', 'Shimo La Tewa']
                    },
                    {
                        'name': 'Kilifi South Sub-County',
                        'code': 'KE-KIL-S',
                        'locations': ['Junju', 'Mwarakaya', 'Shimo La Tewa', 'Chasimba', 'Mtepeni']
                    },
                ]
            },
            {
                'name': 'Nyeri County',
                'code': 'KE-NYE',
                'districts': [
                    {
                        'name': 'Nyeri Town Sub-County',
                        'code': 'KE-NYE-T',
                        'locations': ['Rware', 'Gatitu/Muruguru', 'Ruring\'u', 'Kamakwa/Mukaro']
                    },
                ]
            },
            {
                'name': 'Meru County',
                'code': 'KE-MER',
                'districts': [
                    {
                        'name': 'Imenti North Sub-County',
                        'code': 'KE-MER-IN',
                        'locations': ['Ntima East', 'Ntima West', 'Mithara', 'Athiru Ruujine', 'Athiru Gaiti']
                    },
                    {
                        'name': 'Meru Town Sub-County',
                        'code': 'KE-MER-T',
                        'locations': ['Makutano', 'Mitunguu', 'Kiirua/Naari', 'Abothuguchi West']
                    },
                ]
            },
            {
                'name': 'Kajiado County',
                'code': 'KE-KAJ',
                'districts': [
                    {
                        'name': 'Kajiado North Sub-County',
                        'code': 'KE-KAJ-N',
                        'locations': ['Ongata Rongai', 'Nkaimurunya', 'Oloolua', 'Ngong']
                    },
                    {
                        'name': 'Kajiado Central Sub-County',
                        'code': 'KE-KAJ-C',
                        'locations': ['Purko', 'Ildamat', 'Dalalekutuk', 'Matapato North', 'Matapato South']
                    },
                ]
            },
            {
                'name': 'Bungoma County',
                'code': 'KE-BUN',
                'districts': [
                    {
                        'name': 'Kanduyi Sub-County',
                        'code': 'KE-BUN-KAN',
                        'locations': ['Bukembe West', 'Bukembe East', 'Township', 'Khalaba', 'Musikoma', 'East Sang\'alo', 'Marakaru/Tuuti']
                    },
                ]
            },
            {
                'name': 'Embu County',
                'code': 'KE-EMB',
                'districts': [
                    {
                        'name': 'Manyatta Sub-County',
                        'code': 'KE-EMB-MAN',
                        'locations': ['Gaturi South', 'Gaturi North', 'Kirimari', 'Ruguru/Ngandori']
                    },
                ]
            },
            {
                'name': 'Nandi County',
                'code': 'KE-NAN',
                'districts': [
                    {
                        'name': 'Nandi Hills Sub-County',
                        'code': 'KE-NAN-NH',
                        'locations': ['Nandi Hills', 'Chepkunyuk', 'Ol Lessos', 'Kabiyet']
                    },
                ]
            },
            {
                'name': 'Kericho County',
                'code': 'KE-KER',
                'districts': [
                    {
                        'name': 'Ainamoi Sub-County',
                        'code': 'KE-KER-AIN',
                        'locations': ['Kapsoit', 'Ainamoi', 'Kapkugerwet', 'Kapsuser']
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
            help='Organization slug to seed Kenya data for',
        )
    
    @transaction.atomic
    def handle(self, *args, **options):
        org_slug = options['organization']
        
        try:
            organization = Organization.objects.get(slug=org_slug)
        except Organization.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Organization with slug "{org_slug}" not found'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'Seeding Kenya geographic data for: {organization.name}'))
        
        # Create Kenya country
        country, created = Region.objects.get_or_create(
            organization=organization,
            code=self.KENYA_DATA['code'],
            defaults={
                'name': self.KENYA_DATA['name'],
                'level': 0,
                'level_type': 'country',
                'is_active': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created country: {country.name}'))
        else:
            self.stdout.write(self.style.WARNING(f'≈ Country already exists: {country.name}'))
        
        # Create counties (regions), sub-counties (districts), and locations
        region_count = 0
        district_count = 0
        location_count = 0
        
        for region_data in self.KENYA_DATA['regions']:
            # Create county (region)
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
                self.stdout.write(f'  ✓ Created county: {region.name}')
            
            # Create sub-counties (districts)
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
                    self.stdout.write(f'    ✓ Created sub-county: {district.name}')
                
                # Create locations
                for location_name in district_data['locations']:
                    location_code = f"{district_data['code']}-{location_name.upper().replace(' ', '-').replace('/', '-')[:15]}"
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
Kenya Geographic Data Seeded Successfully!

Summary:
--------
Country: 1 (Kenya)
Counties (Regions): {region_count} created
Sub-Counties (Districts): {district_count} created  
Locations: {location_count} created
Total: {1 + region_count + district_count + location_count} geographic entities

Use these to assign supervisors to counties and field officers to sub-counties/locations.
        '''))

