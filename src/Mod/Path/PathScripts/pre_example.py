# example parser that works with griffin.ncc. It simply parses line over line,
# and if a line doesn't start with a G or M command, the last one is repeated,
# before the line. ensuring that all lines start with a G or M command.

def parse(inputstring):
    "parse(inputstring): returns a parsed outputstring"
    lines = inputstring.split("\n")
    output = ""
    lastcommand = None
    for l in lines:
        l = l.strip()
        if not l:
            # discard empty lines
            continue
        if l[0] in ["(","%"]:
            # discard comment and other non-gcode lines
            continue
        if l[0].upper() in ["G","M"]:
            # found a G or M command: we store it
            output += l + "\n"
            last = l[0].upper()
            for c in l[1:]:
                if not c.isdigit():
                    break
                else:
                    last += c
            lastcommand = last
        elif lastcommand:
            # no G or M command: we repeat the last one
            output += lastcommand + " " + l + "\n"
    return output            

