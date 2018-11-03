
import smart_imports

smart_imports.all()


class Command(django_management.BaseCommand):

    help = 'migrate chronicle to tt_game_chronicle'

    def handle(self, *args, **options):

        total_records = models.Record.objects.all().count()

        for i, record in enumerate(models.Record.objects.all().order_by('created_at')):
            print('process record {}/{}'.format(i, total_records))

            bill_id = None
            tags = set()

            for actor in record.actors.all():
                if actor.bill:
                    bill_id = actor.bill_id
                    tags.add(bills_meta_relations.Bill.create_from_id(actor.bill_id).tag)

                if actor.place:
                    tags.add(places_meta_relations.Place.create_from_id(actor.place_id).tag)

                if actor.person:
                    tags.add(persons_meta_relations.Person.create_from_id(actor.person_id).tag)

            tt_services.chronicle.cmd_add_event(tags=tags,
                                                message=record.text,
                                                attributes={'bill_id': bill_id},
                                                turn=record.created_at_turn,
                                                timestamp=time.mktime(record.created_at.timetuple()))
