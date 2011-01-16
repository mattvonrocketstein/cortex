""" cortex.core.symbols
"""
class Symbols:
    """ central symbol tracker """
    @staticmethod
    def factory(symbol):
        """ """
        def symbol_builder(label):
            """ """
            label = label.replace(' ','_')
            name  = '{symbol}_{label}'
            name  = name.format(symbol=symbol.upper(),
                                label=label.upper())
            val   = getattr(Symbols,symbol).union(set([name]))
            setattr(Symbols, symbol, val)
            return name
        setattr(Symbols, symbol, set())
        setattr(Symbols, '_'+symbol, symbol_builder)
        return symbol_builder

event    = Symbols.factory('event')
command  = Symbols.factory('command')
