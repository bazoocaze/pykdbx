from src import password_generator


def test_generate():
    pass1 = password_generator.generate(10)
    pass2 = password_generator.generate(10)
    assert pass1 != pass2
    assert pass1.__len__() == 10
