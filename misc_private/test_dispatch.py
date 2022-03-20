from functools import singledispatchmethod


class toto:
    def __init__(self):
        pass

    @singledispatchmethod
    def test(self, arg):
        raise NotImplementedError("Cannot test with", a)

    @test.register
    def _(self, arg: int):
         print("test - int", arg)

    @test.register
    def _(self, arg: float):
        print("test - float", arg)
