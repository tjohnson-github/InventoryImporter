

@dataclass
class Department:
    code: int               = field(repr=True)
    name: str               = field(repr=True)
    margin: float           = field(repr=False,default=None)
    formatted_code: str     = field(init=False,repr=False)
    dptStr: str             = field(init=False,repr=False)

    def __post_init__(self):

        if len(str(self.code))==1:
            self.formatted_code = f'00{self.code}'
        else:
            self.formatted_code = f'0{self.code}'

        self.dptStr = f'{self.code} : {self.name}'

    def __str__(self):
        return f'{self.code},{self.name},{self.margin}'

