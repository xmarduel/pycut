from functools import singledispatchmethod


class toto:
    def __init__(self):
        pass

    @singledispatchmethod
    def test(self, arg):
        raise NotImplementedError(f"Cannot run 'toto.test' method with {arg}")

    @test.register
    def _(self, arg: int):
         print(f"test - int {arg}")

    @test.register
    def _(self, arg: float):
        print(f"test - float {arg}")

    @test.register
    def _(self, arg: bool):
        print(f"test - bool {arg}")
