from ply.lex import TOKEN

tokens = [
    "Number",
    "Name",
    "String",
    "Eq",
    "Leq",
    "Req",
]

reserved = {
    "for" : "FOR",
    "in"  : "IN",
    "if"  : "IF",
    "else" : "ELSE",
    "while" : "WHILE",
    "func" : "FUNC",
    "break" : "BREAK",
    "continue" : "CONTINUE",
    "return" : "RETURN",
    "and" : "AND",
    "or" : "OR",
    "not" : "NOT",
    "nil" : "NIL",
    "true" : "TRUE",
    "false" : "FALSE",
    "local" : "LOCAL",
    "winapi": "WINAPI",
    "to_str": "TO_STR",
}

tokens += list(reserved.values())

# winapi('user32.dll', 'FindWindow', [c_char_p, c_char_p], ['sss', 'bbbb'])

# ignore spaces and tab
t_ignore = " \t"

# define comment
def t_COMMENT(t):
    r"\#.*"
    
# define newline
def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)

def t_Number(t):
    r"(\d+\.\d+|\d+\.?|\.\d+)(e[+-]?\d+)?"
    value = eval(t.value)
    t.value = {
        "value" : value,
        "type"  : t.type
    }
    return t

def t_Name(t):
    r"[a-zA-Z_]+\w*"
    # a key word?
    t.type = reserved.get(t.value,\
                          "Name")
    dt = {
        "NIL" : None,
        "FALSE" : False,
        "TRUE" : True,
    }
    value = dt.get(t.type, t.value)
    t.value = {
        "value" : value,
        "type"  : t.type
    }
    return t

# define string rule
escape_char = r"\\."
normal_char = r'[^"\n]'
String = r'"' + r'(' + escape_char + \
         r'|' + normal_char + r')' + \
         r'*' + r'"'
@TOKEN(String)
def t_String(t):
    value = t.value[1:-1]
    # deal escape_char
    escape_char_dt ={
        '\\a' : '\a',
        '\\b' : '\b',
        '\\f' : '\f',
        '\\n' : '\n',
        '\\r' : '\r',
        '\\t' : '\t',
        '\\v' : '\v',
        '\\"' : '"',
    }
    char_list = []
    length = len(value)
    index = 0
    while index < length:
        char = value[index]
        if char == '\\':
            res = escape_char_dt.get(value[index:index+2], None)
            if res:
                char_list.append(res)
                index += 2
                continue
            if value[index+1] == 'x':
                char_list.append(chr(eval(''.join(['0x', value[index+2:index+4]]))))
                index += 4
                continue
        char_list.append(char)
        index += 1
    value = ''.join(char_list)
    t.value = {
        'type' : 'String',
        'value' : value,
    }
    return t

def t_Eq(t):
    r"=="
    return t

def t_Leq(t):
    r"<="
    return t

def t_Req(t):
    r">="
    return t

# literals
literals = ["+", "-", "*", "/", "%", ">",
            "<", "=", ":", ";", "{", "}"
            , "(", ")", "[", "]", ","]

# error handling rule
def t_error(t):
    raise Exception("Illegal character '%s'"
          % t.value[0])

# EOF handling rule
def t_eof(t):
    # Get more input (Example)
    return None
