from lark import Lark, Transformer

ebnf_grammar = r"""
    textfield: entry*

    entry: (segment "//")* flags_segment

    segment: /[^\/]+/

    flags_segment: "W" ("|" "Q")? | "Q" ("|" "W")
    
    %import common.WS
    %ignore WS
"""


class StructuralTransformer(Transformer):
    def segment(self, items):
        return str(items[0]).replace("\xa0", " ").strip()

    def flags_segment(self, tokens):
        val = "".join(str(t) for t in tokens).upper()

        return {
            "is_w": "W" in val,
            "is_q": "Q" in val,
        }

    def entry(self, items):
        flags = items[-1]
        segments = items[:-1]
        return {
            "segments": segments,
            "flags": flags,
        }

    def textfield(self, entries):
        return list(entries)


parser = Lark(ebnf_grammar, start="textfield", parser="lalr", transformer=StructuralTransformer())