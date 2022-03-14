def get_line_given_pos(text, pos):
    text_before = text[:pos+1]
    line_count = len(text_before.splitlines())
    return text.splitlines()[line_count-1]
    
