import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.crossword.variables:
            for word in self.crossword.words:
                # word should fit in length
                if var.length != len(word):
                    self.domains[var].remove(word)
        # raise NotImplementedError

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        overlap = self.crossword.overlaps[x, y]
        if overlap is None:
            return False
        else:
            i, j = overlap
            flag = False
            removables = []
            for wordx in self.domains[x]:
                matchFound = False
                for wordy in self.domains[y]:
                    if wordx[i] == wordy[j]:
                        matchFound = True
                        break
                if not matchFound:
                    # mark those words in a list to remove
                    removables.append(wordx)
                    # changes will be made in x
                    flag = True
            # removing words from x
            for word in removables:
                self.domains[x].remove(word)
            return flag
        # raise NotImplementedError

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is None:
            for x in self.domains.keys():
                for y in self.domains.keys():
                    if x is not y:
                        self.revise(x, y)
        else:
            for arc in arcs:
                x, y = arc
                if self.revise(x, y):
                    # add additional arcs...
                    for ys in self.domains.keys():
                        if x is not ys:
                            arcs.append(x, ys)
                if len(self.domains[x]) == 0:
                    return False
        return True
        # raise NotImplementedError

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # check if all the variables are there in assignment
        return len(self.domains.keys()) == len(assignment.keys())
        #raise NotImplementedError

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # set can be used to check repetition
        if len(assignment.values()) != len(set(assignment.values())):
            return False
        # word should be of same length that of variable
        for key, value in assignment.items():
            if key.length != len(value):
                return False
        # check for binary constraints i.e. common characters should match
        for variables, overlaps in self.crossword.overlaps.items():
            x, y = variables
            if x not in assignment.keys() or y not in assignment.keys():
                continue
            if overlaps is None:
                continue
            i, j = overlaps
            if assignment[x][i] != assignment[y][j]:
                return False
        return True
        #raise NotImplementedError

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # dictionary to store word as key and number of rule-outs as value
        dictionary = {}
        for word in self.domains[var]:
            dictionary[word] = 0
        for pair, overlap in self.crossword.overlaps.items():
            if overlap is None or var not in pair:
                continue
            x, y = pair
            i, j = overlap
            if x is var and y not in assignment.keys():
                for wordx in self.domains[x]:
                    for wordy in self.domains[y]:
                        if wordx[i] != wordy[j]:
                            dictionary[wordx] += 1
            if y is var and x not in assignment.keys():
                for wordy in self.domains[y]:
                    for wordx in self.domains[x]:
                        if wordy[j] != wordx[i]:
                            dictionary[wordy] += 1
        # sort as number of rule-outs in ascending order
        li = sorted(dictionary.items(), key=lambda x:x[1])
        # return words in sorted order
        return map(lambda x:x[0], li)
        # raise NotImplementedError

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # list of variables having minimum number of words
        min_word_var_len = min(len(words) for words in self.domains.values())
        # dict() to contain variable as key and number of neighbours as value
        dictionary_len_neighbours = {}
        # initialize dictionary
        for var in self.crossword.variables:
            if var not in assignment.keys():
                if len(self.domains[var]) == min_word_var_len:
                    dictionary_len_neighbours[var] = 0
        # increment those variables that are in dict() according to number of neighbours
        for var in dictionary_len_neighbours:
            dictionary_len_neighbours[var] += len(self.crossword.neighbors(var))
        # sort by decreasing number of neighbours
        li = sorted(dictionary_len_neighbours.items(),
                    key=lambda x: x[1], reverse=True)
        # follow brute force if list is empty
        if len(li) == 0:
            for var in self.crossword.variables:
                if var not in assignment.keys():
                    return var
        # return first element i.e. the most appropriate variable
        return li[0][0]
        #raise NotImplementedError

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # base case
        if self.assignment_complete(assignment):
            return assignment
        # get suitable variable
        var = self.select_unassigned_variable(assignment)
        # get words in suitable order
        li_words = self.order_domain_values(var, assignment)
        # apply them one by one and see outcomes
        for word in li_words:
            assignment[var] = word
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result is not None:
                    return result
                else:
                    del assignment[var]
            else:
                del assignment[var]
        return None
        #raise NotImplementedError


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
