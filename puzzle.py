from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    # TODO
    # either of one exists not both
    Biconditional(AKnight, Not(AKnave)),  # XOR
    # if statement is true, it implies Knight
    Implication(And(AKnight, AKnave), AKnight),
    # if statement is false, it implies Knave
    Implication(Not(And(AKnight, AKnave)), AKnave)
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    # TODO
    # either of one exists not both
    Biconditional(AKnight, Not(AKnave)),  # XOR
    Biconditional(BKnight, Not(BKnave)),  # XOR
    # if statement is true, it implies Knight
    Implication(And(BKnave, AKnave), AKnight),
    # if statement is false, it implies Knave
    Implication(Not(And(BKnave, AKnave)), AKnave)
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    # TODO
    # either of one exists not both
    Biconditional(AKnight, Not(AKnave)),  # XOR
    Biconditional(BKnight, Not(BKnave)),  # XOR
    # if statement is true, it implies Knight
    Implication(Biconditional(And(AKnight, BKnight), Not(And(AKnave, BKnave))), AKnight),
    Implication(Biconditional(And(AKnight, BKnave), Not(And(AKnave, BKnight))), BKnight),
    # if statement is false, it implies Knave
    Implication(Not(Biconditional(And(AKnight, BKnight), Not(And(AKnave, BKnave)))), AKnave),
    Implication(Not(Biconditional(And(AKnight, BKnave), Not(And(AKnave, BKnight)))), BKnave)
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    # TODO
    # either of one exists not both
    Biconditional(AKnight, Not(AKnave)),  # XOR
    Biconditional(BKnight, Not(BKnave)),  # XOR
    Biconditional(CKnight, Not(CKnave)),  # XOR
    # if statement is true, it implies Knight
    Implication(Biconditional(AKnight, Not(AKnave)), AKnight),
    # checking identity of C and compairing statement of A to that of B...
    Implication(And(CKnave, Implication(Biconditional(AKnight, Not(AKnave)), AKnave)), BKnight),
    Implication(AKnight, CKnight),
    # if statement is false, it implies Knave
    Implication(Not(Biconditional(AKnight, Not(AKnave))), AKnave),
    Implication(And(Not(CKnave), Not(Implication(Biconditional(AKnight, Not(AKnave)), AKnave))), BKnave),
    Implication(Not(AKnight), CKnave),
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
