
import smart_imports

smart_imports.all()


def check_road_correctness(place_1, place_2, path):
    path_suitables = roads_logic.is_path_suitable_for_road(start_x=place_1.x,
                                                           start_y=place_1.y,
                                                           path=path)

    if not path_suitables.is_NO_ERRORS:
        raise django_forms.ValidationError(path_suitables.text)

    cells = roads_logic.get_path_cells(start_x=place_1.x,
                                       start_y=place_1.y,
                                       path=path)

    if places_storage.places.get_by_coordinates(*cells[-1]).id != place_2.id:
        raise django_forms.ValidationError('Указанный путь заканчивается не в том городе')
