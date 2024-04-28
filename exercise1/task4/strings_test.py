#!/usr/bin/env python3
import io
import os
import sys
import importlib
import textwrap
import numpy as np
import math as m
import multiprocessing as mp
import ast
import pprint
import importlib.util
import time
import math
import numbers

max_points = 0
obtained_points = 0
default_permitted_modules = ["matplotlib",
                             "matplotlib.pyplot",
                             "matplotlib.widgets",
                             "functools",
                             "mpl_toolkits.mplot3d"]
timeout = 60
numeric_accuracy = 1e-6
int_accuracy = 0

registered_tests = dict()


def info(string):
    print(string)


def format_beautifully(*blocks):
    # step #1: convert short atomics to wrap statements
    preprocessed_blocks = []
    for (kind, object) in blocks:
        if kind == 'wrap':
            preprocessed_blocks += [(kind, str(object))]
        elif (kind == 'atomic') or (kind == 'args'):
            string = pprint.pformat(object, width=79)
            if kind == 'args':
                string = "(" + string[1:-1] + ")"
            if '\n' in string:
                preprocessed_blocks += [('atomic', string)]
            else:
                preprocessed_blocks += [('wrap', string)]

    # step #2: merge consecutive wrap statements
    merged_blocks = []
    wrap_strings = []
    for (kind, string) in preprocessed_blocks:
        if kind == 'wrap':
            wrap_strings += [string]
        elif kind == 'atomic':
            merged_blocks += [('wrap', "".join(wrap_strings))]
            wrap_strings = []
            merged_blocks += [(kind, string)]
    merged_blocks += [('wrap', "".join(wrap_strings))]

    # step #3: combine the text blocks
    #          in particular merge atomics followed by wrap text
    lines = []
    for (kind, string) in merged_blocks:
        if kind == 'wrap':
            if not lines:
                lines += textwrap.fill(string, width=79).splitlines()
            else:
                indent = len(lines[-1]) if lines else 0
                new_lines = textwrap.fill("#" * indent + string, width=79).splitlines()
                lines[-1] = new_lines[0].replace("#" * indent, lines[-1])
                lines += new_lines[1:]
        elif kind == 'atomic':
            lines += string.splitlines()

    return "\n".join(lines)


def type_equal(a, b):
    # surprise #1: numpy.int64 and the like are not of type integer!
    # surprise #2: numpy.float64 and Python float are disjoint!
    def denumpify(x):
        return x.item() if isinstance(x, np.generic) else x

    return type(denumpify(a)) == type(denumpify(b))


def equal(a, b):
    if not type_equal(a, b):
        return False
    if isinstance(a, int):
        return abs(a - b) <= int_accuracy
    if isinstance(a, float):
        return abs(a - b) < numeric_accuracy
    if isinstance(a, np.poly1d):
        return equal(a.c, b.c)
    if isinstance(a, np.ndarray):
        if a.shape != b.shape: return False
        if a.size == 0: return True
        return np.amax(abs(a.astype(np.float64) - b.astype(np.float64))) < numeric_accuracy
    if isinstance(a, tuple) or isinstance(a, list):
        if len(a) != len(b): return False
        for (a, b) in zip(a, b):
            if not equal(a, b): return False
        return True
    return a == b


class CheckFailure(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return format_beautifully(('wrap', self.message))


class Timeout(CheckFailure):
    def __init__(self, call):
        self.call = call

    def __str__(self):
        (fname, *args) = self.call
        blocks = [('wrap', "Der Aufruf {}".format(fname)),
                  ('args', args),
                  ('wrap', " terminiert nicht, oder ist SEHR ineffizient.")]
        return format_beautifully(*blocks)


class WrongOutput(CheckFailure):
    def __init__(self, call, expected_result, obtained_result):
        self.call = call
        self.expected_result = expected_result
        self.obtained_result = obtained_result

    def __str__(self):
        (fname, *args) = self.call
        blocks = [('wrap', "Der Aufruf {}".format(fname)),
                  ('args', args)]
        if isinstance(self.obtained_result, Exception):
            blocks += ([('wrap', " liefert den Fehler: "),
                        ('atomic', self.obtained_result)])
        elif isinstance(self.obtained_result, type(None)):
            blocks += ([('wrap', " hat keine Ausgabe, sollte aber "),
                        ('atomic', self.expected_result),
                        ('wrap', " ausgeben.")])
        else:
            blocks += ([('wrap', " liefert die Ausgabe "),
                        ('atomic', self.obtained_result),
                        ('wrap', ", richtig wäre aber "),
                        ('atomic', self.expected_result),
                        ('wrap', ".")])
        return format_beautifully(*blocks)


class WrongResult(CheckFailure):
    def __init__(self, call, expected_result, obtained_result):
        self.call = call
        self.expected_result = expected_result
        self.obtained_result = obtained_result

    def __str__(self):
        (fname, *args) = self.call
        blocks = [('wrap', "Der Aufruf {}".format(fname)),
                  ('args', args)]
        if isinstance(self.obtained_result, Exception):
            blocks += ([('wrap', " liefert den Fehler: "),
                        ('atomic', self.obtained_result)])
        elif isinstance(self.obtained_result, type(None)):
            blocks += ([('wrap', " hat keinen Rückgabewert, sollte aber "),
                        ('atomic', self.expected_result),
                        ('wrap', " zurückgeben.")])
        elif not type_equal(self.obtained_result, self.expected_result):
            blocks += ([('wrap', " liefert ein Ergebnis vom Typ "),
                        ('wrap', "'" + type(self.obtained_result).__name__ + "'"),
                        ('wrap', ", erwartet wird aber ein Ergebnis vom Typ "),
                        ('wrap', "'" + type(self.expected_result).__name__ + "'.")])
        else:
            blocks += ([('wrap', " liefert das Ergebnis "),
                        ('atomic', self.obtained_result),
                        ('wrap', ", richtig wäre aber "),
                        ('atomic', self.expected_result),
                        ('wrap', ".")])
        return format_beautifully(*blocks)


class AstInspector(ast.NodeVisitor):
    def __init__(self, file="<unknown>", imports=[]):
        self.file = file
        self.permitted_modules = set(default_permitted_modules + imports)
        self.errors = []

    def check_module(self, module):
        if module in self.permitted_modules: return
        self.errors.append(CheckFailure("Das Modul {} darf für diese "
                                        "Aufgabe nicht verwendet werden."
                                        .format(module)))

    def visit_Import(self, node):
        for m in [n.name for n in node.names]:
            self.check_module(m)

    def visit_ImportFrom(self, node):
        self.check_module(node.module)


def subprocess_eval(queue, proc_id, expr, module):
    stdout = sys.stdout
    with io.StringIO() as output:
        sys.stdout = output
        try:
            m = importlib.import_module(module)
            (f, *args) = map(lambda x: eval(x, vars(m)) if isinstance(x, str) else x, expr)
            result = f(*args)
        except BaseException as e:
            result = e
        queue.put((proc_id, result, output.getvalue()))
    sys.stdout = stdout


def check_calls(forms, module_name):
    check_output = forms and len(forms[0]) == 3
    if check_output:
        calls, desired_results, desired_outputs = zip(*forms) if forms else ([], [], [])
    else:
        calls, desired_results = zip(*forms) if forms else ([], [])
    queue = mp.Queue()
    processes = []
    process_ids = set(range(len(calls)))
    for pid in process_ids:
        p = mp.Process(target=subprocess_eval,
                       args=(queue, pid, calls[pid], module_name))
        p.start()
        processes.append(p)

    queue_contents = []
    try:
        for _ in process_ids:
            queue_contents.append(queue.get(True, timeout))
    except:
        pass
    finally:
        for p in processes: p.terminate()

    for pid in process_ids:
        match = [result for (id, result, _) in queue_contents if id == pid]
        matchOutput = [out.strip() for (id, _, out) in queue_contents if id == pid]
        if not match:
            yield Timeout(calls[pid])
        elif not equal(desired_results[pid], match[0]):
            yield WrongResult(calls[pid], desired_results[pid], match[0])
        elif check_output and not equal(desired_outputs[pid], matchOutput[0]):
            yield WrongOutput(calls[pid], desired_outputs[pid], matchOutput[0])


def check_module(module_name, imports=[], calls=[], nuke=[], inttol=0):
    try:
        int_accuracy = inttol
        spec = importlib.util.find_spec(module_name)
        if not spec:
            yield CheckFailure("Die Datei {}.py konnte nicht gefunden werden. "
                               "Sie sollte im selben Ordner liegen wie "
                               "dieses Programm.".format(module_name))
            return

        with open(spec.origin, 'r', encoding='utf-8') as f:
            source = f.read()
        st = ast.parse(source, spec.origin)
        inspector = AstInspector(spec.origin, imports)
        inspector.visit(st)
        errors = inspector.errors or check_calls(calls, module_name)
        for error in errors: yield error
    except OSError:
        yield CheckFailure("Die Datei {} konnte nicht geöffnet werden."
                           .format(spec.origin))
    except SyntaxError as e:
        yield CheckFailure("Die Datei {} enthält einen Syntaxfehler "
                           "in Zeile {:d}."
                           .format(spec.origin, e.lineno))
    except CheckFailure as e:
        yield e
    except Exception as e:
        yield CheckFailure("Beim Laden des Moduls {} ist ein Fehler "
                           "vom Typ '{}' aufgetreten."
                           .format(module_name, str(e)))


def register(name, description, points, module, **kwargs):
    registered_tests[name] = (description, points, module, kwargs)


def check(description, points, module, **kwargs):
    global max_points
    global obtained_points

    pstr = ("1 Punkt" if points == 1 else f"{points:.2f} Punkte")
    desc = description + " (" + pstr + ")"
    max_points += points
    info("=" * (len(desc) + 2))
    info(" " + desc)
    info("=" * (len(desc) + 2))

    try:
        stdout, stderr = sys.stdout, sys.stderr
        try:
            with open(os.devnull, 'w') as f:
                sys.stdout, sys.stderr = f, f
                errors = list(check_module(module, **kwargs))
        finally:
            sys.stdout, sys.stderr = stdout, stderr
    except BaseException as e:
        info("Eine unbehandelte Ausnahme ist aufgetreten: '{}'"
             .format(str(e)))
    else:
        if errors:
            for e in errors: info(str(e))
            info("Diese Teilaufgabe enthält Fehler!")
        elif not kwargs["calls"]:
            max_points -= points
            info("Diese Teilaufgabe hat keine öffentlichen Testcases.")
        else:
            obtained_points += points
            info("Super! Alles scheint zu funktionieren.")
    info("")


parts_cmdline = []


def check_from_cmdline():
    global parts_cmdline
    parts = sys.argv[1:]
    parts = [p.lower() for p in parts]
    if len(parts) == 0:
        parts = registered_tests.keys()
    else:
        parts_cmdline = parts

    for part in parts:
        if part not in registered_tests:
            info(f"Teilaufgabe '{part}' gibt es nicht.")
            info(f"Vorhandene Teilaufgaben: {', '.join(registered_tests.keys())}.")
            sys.exit(1)

    for part in parts:
        description, points, module, kwargs = registered_tests[part]
        check(description, points, module, **kwargs)


def import_modules(modules):
    for module in modules:
        importlib.import_module(module)


def compute_process_spawn_time():
    start = time.time()
    p = mp.Process(target=import_modules, args=(default_permitted_modules,))
    p.start()
    p.join()
    end = time.time()
    return math.ceil(end - start)


def report():
    if len(parts_cmdline) != 0:
        print(f"Teilaufgabe{'n' if len(parts_cmdline) > 1 else ''} {', '.join(parts_cmdline)}: ", end="")
        print(f"{obtained_points:g} von {max_points:g} Punkten.")
    else:
        print(f"Insgesamt: {obtained_points:g} von {max_points:g} Punkten.")


if __name__ == "__main__":
    mp.freeze_support()
    timeout = 2 * compute_process_spawn_time() + 9

    ###############################
    ## Nun die eigentlichen Checks
    ###############################
    register("a", "Aufgabe 4a: Enthält meine Zeichenkette ein bestimmtes Zeichen?", 0.125,
             "strings",
             imports=[],
             calls=[
                 (("contains_char", "'U$:E<t'", "'Y'"), False),
                 (("contains_char", "'v<3:V'", "'m'"), False),
                 (("contains_char", "',2&RO.v[{vAowY,6yS'", "'+'"), False),
                 (("contains_char", "',K3,b90t{f$5~C0eUHn'", "'q'"), False),
                 (("contains_char", "'nyCS'", "'!'"), False),
                 (("contains_char", "'x&WS9J&l1UQ2'", "'V'"), False),
                 (("contains_char", "'(U-\\LJzehD#K,$wNBUu;.~W>S3s3i'", "'B'"), True),
                 (("contains_char", "'%a{gdN`slOCC$.vv<$|aND,}!Tm2'", "'y'"), False),
                 (("contains_char", "'O+s/>MOl,'", "']'"), False),
                 (("contains_char", "'++hBv)<c'", "'P'"), False),
                 (("contains_char", "'p(cLIR.<v)S38e,_&pSup=b$I/='", "'V'"), False),
                 (("contains_char", "'6NutdCOuQzEG<(WJocX6BD,e]lk'", "'G'"), True),
                 (("contains_char", "'&~^!k3dtE'", "'S'"), False),
                 (("contains_char", "'Qg_Z/vNHTBdlbG]'", "'!'"), False),
                 (("contains_char", "'=(V?UValev'", "'Y'"), False),
                 (("contains_char", "',Psty(JPj%%MFE[HErgVN(h*yn8T'", "'('"), True),
                 (("contains_char", "'w*]b5vZ<wWw7XKRb+Qh[J{/gSjg,_'", "'b'"), True),
                 (("contains_char", "'@,9|-k~OsIC,%1j28.bR/|7nnT{'", "'4'"), False),
                 (("contains_char", "'.z%90d57%&}B{_z(Q]&=|K'", "'C'"), False),
                 (("contains_char", "''", "'>'"), False),
                 (("contains_char", "'*:`^}6]r/%aKJQFN%C*'", "'P'"), False),
                 (("contains_char", "'h^97W2Mg-f},k>`'", "'M'"), True),
                 (("contains_char", "'Q)k?(BMh]?TWIu#1.erd-9{x|DY'", "'['"), False),
                 (("contains_char", "'mp%>YNyg#+^w=##=*T)(%6?$t3@L.P]'", "'S'"), False),
                 (("contains_char", "'lJ-+w{C2<paTLJ|+l6.q%JTZ'", "'r'"), False),
                 (("contains_char", "'k|_EL#&=}h'", "'j'"), False),
                 (("contains_char", "'/{>S)MkE|9U=XzLv=<]'", "'}'"), False),
                 (("contains_char", "'xW]=J>_WWMVR:]D2?/+'", "'@'"), False),
                 (("contains_char", "'z#QHmz/AQiq>d'", "'d'"), True),
                 (("contains_char", "'oFKxtGlv:t92I*q,'", "'Z'"), False),
                 (("contains_char", "'3xg~~~}E@=/:G'", "'H'"), False),
             ])
    register("b", "Aufgabe 4b: Palindrome", 0.125, "strings",
             imports=[],
             calls=[
                 (("is_palindrome", "'never odd or even'"), True),
                 (("is_palindrome", "'top spot'"), True),
                 (("is_palindrome", "'ABBA'"), True),
                 (("is_palindrome", "'taco o cat'"), True),
                 (("is_palindrome", "'ABB'"), False),
             ])
    register("c", "Aufgabe 4c: Count Char Frequency", 0.125, "strings",
             calls=[
                 (("count_char_frequency", "'ABBA'"), {"A": 2, "B": 2}),
                 (("count_char_frequency", "'n{Yv)@'"), {'n': 1, '{': 1, 'Y': 1, 'v': 1, ')': 1, '@': 1}),
                 (("count_char_frequency", "'uI080'"), {'u': 1, 'I': 1, '0': 2, '8': 1}),
                 (("count_char_frequency", "'WFuZg0>D4-:'"),
                  {'W': 1, 'F': 1, 'u': 1, 'Z': 1, 'g': 1, '0': 1, '>': 1, 'D': 1, '4': 1, '-': 1, ':': 1}),
                 (("count_char_frequency", "'1Z,Cj:}'"), {'1': 1, 'Z': 1, ',': 1, 'C': 1, 'j': 1, ':': 1, '}': 1}),
                 (("count_char_frequency", "'m%lqbv0?F4\*/Dj'"),
                  {'m': 1, '%': 1, 'l': 1, 'q': 1, 'b': 1, 'v': 1, '0': 1, '?': 1, 'F': 1, '4': 1, '\\': 1, '*': 1,
                   '/': 1, 'D': 1, 'j': 1}),
                 (("count_char_frequency", "'>L|B!t[uU#m5'"),
                  {'>': 1, 'L': 1, '|': 1, 'B': 1, '!': 1, 't': 1, '[': 1, 'u': 1, 'U': 1, '#': 1, 'm': 1, '5': 1}),
                 (("count_char_frequency", "'bdZBiDF'"), {'b': 1, 'd': 1, 'Z': 1, 'B': 1, 'i': 1, 'D': 1, 'F': 1}),
                 (("count_char_frequency", "':+2'"), {':': 1, '+': 1, '2': 1}),
                 (("count_char_frequency", "'@?WR<4'"), {'@': 1, '?': 1, 'W': 1, 'R': 1, '<': 1, '4': 1}),
                 (("count_char_frequency", "'}2NA*0'"), {'}': 1, '2': 1, 'N': 1, 'A': 1, '*': 1, '0': 1}),
                 (("count_char_frequency", "'h0E.p\jh/'"),
                  {'h': 2, '0': 1, 'E': 1, '.': 1, 'p': 1, '\\': 1, 'j': 1, '/': 1}),
                 (("count_char_frequency", "'X~yBV-IZ6+YC:U'"),
                  {'X': 1, '~': 1, 'y': 1, 'B': 1, 'V': 1, '-': 1, 'I': 1, 'Z': 1, '6': 1, '+': 1, 'Y': 1, 'C': 1,
                   ':': 1, 'U': 1}),
                 (("count_char_frequency", "'f!O'"), {'f': 1, '!': 1, 'O': 1}),
                 (("count_char_frequency", "'NMiYLzY@-/M3.Z'"),
                  {'N': 1, 'M': 2, 'i': 1, 'Y': 2, 'L': 1, 'z': 1, '@': 1, '-': 1, '/': 1, '3': 1, '.': 1, 'Z': 1}),
                 (("count_char_frequency", "':oc#'"), {':': 1, 'o': 1, 'c': 1, '#': 1}),
                 (("count_char_frequency", "''"), {}),
                 (("count_char_frequency", "'i;ZS=*)ZW'"),
                  {'i': 1, ';': 1, 'Z': 2, 'S': 1, '=': 1, '*': 1, ')': 1, 'W': 1}),
                 (("count_char_frequency", "'(,|'"), {'(': 1, ',': 1, '|': 1}),
                 (("count_char_frequency", "'zLpknQ/x!+kMz3i'"),
                  {'z': 2, 'L': 1, 'p': 1, 'k': 2, 'n': 1, 'Q': 1, '/': 1, 'x': 1, '!': 1, '+': 1, 'M': 1, '3': 1,
                   'i': 1}),
                 (("count_char_frequency", "'5dUC{Pm[9UXI'"),
                  {'5': 1, 'd': 1, 'U': 2, 'C': 1, '{': 1, 'P': 1, 'm': 1, '[': 1, '9': 1, 'X': 1, 'I': 1}),
                 (("count_char_frequency", "'[x-oB'"), {'[': 1, 'x': 1, '-': 1, 'o': 1, 'B': 1}),
                 (("count_char_frequency", "'Ja>umPDNZ'"),
                  {'J': 1, 'a': 1, '>': 1, 'u': 1, 'm': 1, 'P': 1, 'D': 1, 'N': 1, 'Z': 1}),
                 (("count_char_frequency", "'Mi%]v|VHa-'"),
                  {'M': 1, 'i': 1, '%': 1, ']': 1, 'v': 1, '|': 1, 'V': 1, 'H': 1, 'a': 1, '-': 1}),
                 (("count_char_frequency", "'FJiZ<'"), {'F': 1, 'J': 1, 'i': 1, 'Z': 1, '<': 1}),
             ])
    register("d", "Aufgabe 4d: First Non-Repeating Char", 0.125, "strings",
             calls=[
                 (("first_non_repeating_char", "''", False), None),
                 (("first_non_repeating_char", "'Y'", True), None),
                 (("first_non_repeating_char", "''", True), None),
                 (("first_non_repeating_char", "'J'", False), 'J'),
                 (("first_non_repeating_char", "'1,EM,Lq'", False), '1'),
                 (("first_non_repeating_char", "'9+3SMCD/$+5G#]'", False), '9'),
                 (("first_non_repeating_char", "']6I4\e'", True), None),
                 (("first_non_repeating_char", "'?y~M$W~*Kg]1]I'", True), '~'),
                 (("first_non_repeating_char", "'hXCxv2\@Mj|'", True), None),
                 (("first_non_repeating_char", "'@m?'", True), None),
                 (("first_non_repeating_char", "'@EsE!{w-'", False), '@'),
                 (("first_non_repeating_char", "'Eb)@E[W97Nutz~b'", False), ')'),
                 (("first_non_repeating_char", "'|NES{//%kaqzz$E'", True), 'E'),
                 (("first_non_repeating_char", "'LjR%Ruj:WZ'", False), 'L'),
                 (("first_non_repeating_char", "',4Zc<'", True), None),
                 (("first_non_repeating_char", "'p=mS{'", True), None),
                 (("first_non_repeating_char", "'/+H[yqv0'", False), '/'),
                 (("first_non_repeating_char", "'4>'", True), None),
                 (("first_non_repeating_char", "'WC=S^QzD'", True), None),
                 (("first_non_repeating_char", "'r%/f%z'", True), '%'),
                 (("first_non_repeating_char", "'1j7haYStE&'", True), None),
                 (("first_non_repeating_char", "';fwFPi^?Cqkr3'", True), None),
                 (("first_non_repeating_char", "'bMso5Bw&A2kKIC'", False), 'b'),
                 (("first_non_repeating_char", "'ceI'", True), None),
                 (("first_non_repeating_char", "',COZ_<'", False), ','),
             ])
    register("e", "Aufgabe 4e: Rotierende Zeichenketten", 0.25, "strings",
             calls=[(('rotate_string', "'ABBA'", 0, 0), 'ABBA'),
                    (('rotate_string', "'HELLO'", 1, 3), 'LOHEL'),
                    (('rotate_string', "':8t3+USU8YN0j2qIB>'", 1, 2), '>:8t3+USU8YN0j2qIB'),
                    (('rotate_string', "'E4VV[xVS1a9*Yq9g!d'", 4, 1), 'V[xVS1a9*Yq9g!dE4V'),
                    (('rotate_string', "'[6V%jIaz-6F6%mB'", 0, 0), '[6V%jIaz-6F6%mB'),
                    (('rotate_string', "'4iZhl4UY:'", 1, 0), 'iZhl4UY:4'),
                    (('rotate_string', "'j]?&;&5(k*~do'", 1, 1), 'j]?&;&5(k*~do'),
                    (('rotate_string', "'8Fl,:'", 1, 2), ':8Fl,'),
                    (('rotate_string', "'nghmy'", 4, 4), 'nghmy'),
                    (('rotate_string', "'_ClEL@q|w$w._.ReR;.'", 3, 2), 'ClEL@q|w$w._.ReR;._'),
                    (('rotate_string', "'A8*Or>V@h'", 0, 2), '@hA8*Or>V'),
                    (('rotate_string', "'uBuWsYd:![CC6h<['", 2, 0), 'uWsYd:![CC6h<[uB'),
                    (('rotate_string', "']PpGxG%R'", 4, 2), 'pGxG%R]P'),
                    (('rotate_string', "'4G3-\\wy~e?Axl(d!g'", 2, 0), '3-\\wy~e?Axl(d!g4G'),
                    (('rotate_string', "',7,5{LOG|:fG*'", 4, 4), ',7,5{LOG|:fG*'),
                    (('rotate_string', "'klkt|i){U{*9X2~!niH'", 3, 1), 'kt|i){U{*9X2~!niHkl'),
                    (('rotate_string', "'yN!|V7@:<9'", 4, 0), 'V7@:<9yN!|'),
                    (('rotate_string', "'f@{(vieL#K~T>k,E@'", 2, 0), '{(vieL#K~T>k,E@f@'),
                    (('rotate_string', "'1C@$p:kvHLb.'", 1, 4), 'Lb.1C@$p:kvH'),
                    (('rotate_string', "'>J{piWd:kC8k((>M90I'", 4, 2), '{piWd:kC8k((>M90I>J'),
                    (('rotate_string', "'.7)vE^6C~Dhh'", 3, 1), ')vE^6C~Dhh.7'),
                    (('rotate_string', "'F[HP4fXcZv$'", 2, 1), '[HP4fXcZv$F'),
                    (('rotate_string', "'-)=PX^Jd@|'", 3, 4), '|-)=PX^Jd@'),
                    (('rotate_string', "'U65-:*G.nAGO=rm'", 3, 4), 'mU65-:*G.nAGO=r'),
                    (('rotate_string', "'.Lnv$[kyUEDIX'", 1, 4), 'DIX.Lnv$[kyUE'),
                    ])
    register("f", "Aufgabe 4f: Rotationsäquivalenz", 0.25, "strings",
             calls=[
                 (("rotationally_equivalent", "''", "''"), True),
                 (("rotationally_equivalent", "'ABBA'", "'BAAB'"), True),
                 (("rotationally_equivalent", "'HELLO'", "'LLOHE'"), True),
                 (("rotationally_equivalent", "'LISTE'", "'ELIST'"), True),
                 (("rotationally_equivalent", "'TAUTAU'", "'UTAUTA'"), True),
                 (("rotationally_equivalent", "'ABBA'", "'BABA'"), False),
             ])

    check_from_cmdline()
    report()
