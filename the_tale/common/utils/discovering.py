# coding: utf-8


def discover_classes(classes_list, base_class):
    return ( class_
             for class_ in classes_list
             if isinstance(class_, type) and issubclass(class_, base_class) and class_ != base_class)
