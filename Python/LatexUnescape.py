import codecs
import re


def tex_escape(text):
    """
        :param text: a plain text message
        :return: the message escaped to appear correctly in LaTeX
    """
    conv = {
        r'\&':  '&',
        r'\%':  '%',
        r'\$':  '$',
        r'\#':  '#',
        r'\_':  ':',
        r'\{':  '{',
        r'\}':  '}',
        r'\textasciitilde{}': '~',
        r'\^{}': '^',
        r'\textbackslash{}': '\\',
        r'\textless{}': '<',
        r'\textgreater{}': '>',
    }
    regex = re.compile('|'.join(re.escape(str(key))
                       for key in sorted(conv.keys(), key=lambda item: - len(item))))
    return regex.sub(lambda match: conv[match.group()], text)


def unescape_latex(input_string):
    pattern = r'\\\\'

    # Use re.sub to find and replace LaTeX commands while preserving backslashes
    unescaped_string = re.sub(pattern, r'\\', input_string)

    return unescaped_string


# Test the function
latex_string = "If $\\angle ABC$ is a straight angle, give the number of degrees in the measure of $\\angle ABD$. [asy] pair A,B,C,D; A = dir(180); D = dir(60); C = dir(0);\ndraw(B--1.2*A,EndArrow); draw(B--1.2*D,EndArrow); label(\"A\",A,S); dot(A);\nlabel(\"B\",B,S); draw(B--1.2*C,EndArrow); label(\"C\",C,S); label(\"D\",D,dir(135));\nlabel(\"$6x^{\\circ}$\",B,NW); label(\"$3x^{\\circ}$\",B+.1,NE); dot(D); dot(C);\n[/asy]"
unescaped = unescape_latex(latex_string)
print(unescaped)
