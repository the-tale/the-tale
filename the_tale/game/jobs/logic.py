# coding: utf-8



def job_power(objects_number, power):
    # На примере Мастеров, пусть:
    # M — количество Мастеров в городе
    # P — доля влияния Мастера (от 0 до 1)
    # Тогда,  коофициент = P / (1/M) = P * M
    return objects_number * power
