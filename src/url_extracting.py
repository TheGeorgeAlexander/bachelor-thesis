import re
from urllib.parse import urlparse



def extract_comment_urls(code, programming_language):
    """
    Returns a list of all URLs found in the comments of the code. Throws an error if
    the programming language is not supported.
    """
    comments = extract_comments(code, programming_language)
    url_regex = r"https?:\/\/(?:\w+:\w+@)?(?:[\d.]{7,15}|\[[:\da-f]{3,39}\]|[a-z\d][a-z\d\-.]{0,252})(?::\d{1,5})?(?:\/[\w\-.~!$&'()*+,;%=:@?#]*)+"

    urls = []
    for comment in comments:
        for url in re.findall(url_regex, comment, re.IGNORECASE):
            parsed_url = urlparse(url)
            urls.append((url, parsed_url.scheme, parsed_url.netloc, parsed_url.path, parsed_url.query, parsed_url.fragment))

    return urls



def extract_comments(code, programming_language):
    """
    Returns a list of all comments in the code. Throws an error if
    the programming language is not supported.
    """
    
    # Some programming languages have the same syntax for comments, they are grouped together
    match programming_language:
        # Single-line: // .....
        # Multi-line:  /* ..... */
        case "C" | "Java" | "C++" | "JavaScript" | "Go" | "TypeScript":
            comments = extract_c_comments(code)

        # Single-line: // .....
        # Single-line: # .....
        # Multi-line:  /* ..... */
        case "PHP":
            comments = extract_php_comments(code)

        # Single-line: # .....
        # Multi-line: <NO CODE HERE> """ ..... """
        # If there is anyting before multi-line, don't extract because it's a string
        case "Python":
            comments = extract_python_comments(code)

        # Single-line: # .....
        # Multi-line: =begin ..... =end
        case "Ruby":
            comments = extract_ruby_comments(code)
        
        # Unsupported language
        case _:
            raise ValueError(f"Can't extract comments because {programming_language} isn't a supported language.")

    return comments



def extract_c_comments(code):
    """
    Extracts the comments of C code:
    - Single-line: // .....
    - Multi-line:  /* ..... */
    """
    comments = []

    # Move through the string and get comments
    i = 0
    in_string = False
    string_terminator = ""
    while i < len(code):
        if in_string:
            # Escaped character in string
            if code[i] == "\\":
                i += 2

            # End of string
            elif code[i] == string_terminator:
                i += 1
                in_string = False
                string_terminator = ""

            else:
                i += 1

        # Start of string
        elif code[i] == "\"" or code[i] == "'":
            in_string = True
            string_terminator = code[i]
            i += 1

        # Single-line comment
        elif code[i:i+2] == "//":
            i += 2
            comment_start = i

            # Move until the end of the line and add to the list
            while i < len(code) and code[i] != '\n':
                i += 1
            comments.append(code[comment_start:i].strip())


        # Multi-line comment
        elif code[i:i+2] == "/*":
            i += 2
            comment_start = i

            # Move until the end of the comment and add to the list
            while i < len(code) - 1 and code[i:i+2] != "*/":
                i += 1
            comments.append(code[comment_start:i].strip())
            i += 2


        else:
            i += 1

    return comments



def extract_php_comments(code):
    """
    Extracts the comments of PHP code:
    - Single-line: // .....
    - Single-line: # .....
    - Multi-line:  /* ..... */
    """
    comments = []

    # Move through the string and get comments
    i = 0
    in_string = False
    string_terminator = ""
    while i < len(code):
        if in_string:
            # Escaped character in string
            if code[i] == "\\":
                i += 2

            # End of string
            elif code[i] == string_terminator:
                i += 1
                in_string = False
                string_terminator = ""

            else:
                i += 1

        # Start of string
        elif code[i] == "\"" or code[i] == "'":
            in_string = True
            string_terminator = code[i]
            i += 1

        # Single-line comment
        elif code[i] == "#" or code[i:i+2] == "//":
            if code[i] == "#":
                i += 1
            else:
                i += 2
            comment_start = i

            # Move until the end of the line and add to the list
            while i < len(code) and code[i] != '\n':
                i += 1
            comments.append(code[comment_start:i].strip())


        # Multi-line comment
        elif code[i:i+2] == "/*":
            i += 2
            comment_start = i

            # Move until the end of the comment and add to the list
            while i < len(code) - 1 and code[i:i+2] != "*/":
                i += 1
            comments.append(code[comment_start:i].strip())
            i += 2


        else:
            i += 1

    return comments



def extract_python_comments(code):
    # Extracts the comments of Python code.
    # If there is anyting before multi-line, don't extract because it's a string.
    # - Single-line: # .....
    # - Multi-line: <NO CODE HERE> """ ..... """
    comments = []

    # Used to determine if a multi-line string should be treated as comment
    has_seen_code_on_line = False

    # Move through the string and get comments
    i = 0
    in_string = False
    string_terminator = ""
    while i < len(code):
        if in_string:
            # Escaped character in string
            if code[i] == "\\":
                i += 2

            # End of string
            elif code[i] == string_terminator:
                i += 1
                in_string = False
                string_terminator = ""

            else:
                i += 1

        # Start of string
        elif code[i] == "\"" or code[i] == "'":
            in_string = True
            string_terminator = code[i]
            i += 1

        # Single-line comment
        elif code[i] == "#":
            i += 1
            comment_start = i

            # Move until the end of the line and add to the list
            while i < len(code) and code[i] != '\n':
                i += 1
            comments.append(code[comment_start:i].strip())
            has_seen_code_on_line = False


        # Multi-line comment
        elif not has_seen_code_on_line and code[i:i+3] == "\"\"\"":
            i += 3
            comment_start = i

            # Move until the end of the comment and add to the list
            while i < len(code) - 2 and code[i:i+3] != "\"\"\"":
                i += 1
            comments.append(code[comment_start:i].strip())
            i += 3


        else:
            # Track if we've seen code characters on this line
            if code[i] == "\n":
                has_seen_code_on_line = False
            elif code[i] != " " and code[i] != "\t":
                has_seen_code_on_line = True

            i += 1

    return comments



def extract_ruby_comments(code):
    """
    Extracts the comments of Ruby code:
    - Single-line: # .....
    - Multi-line:  =begin ..... =end
    """
    comments = []

    # Move through the string and get comments
    i = 0
    in_string = False
    string_terminator = ""
    while i < len(code):
        if in_string:
            # Escaped character in string
            if code[i] == "\\":
                i += 2

            # End of string
            elif code[i] == string_terminator:
                i += 1
                in_string = False
                string_terminator = ""

            else:
                i += 1

        # Start of string
        elif code[i] == "\"" or code[i] == "'":
            in_string = True
            string_terminator = code[i]
            i += 1

        # Single-line comment
        elif code[i] == "#":
            i += 1
            comment_start = i

            # Move until the end of the line and add to the list
            while i < len(code) and code[i] != '\n':
                i += 1
            comments.append(code[comment_start:i].strip())


        # Multi-line comment
        elif code[i:i+6] == "=begin":
            i += 6
            comment_start = i

            # Move until the end of the comment and add to the list
            while i < len(code) - 3 and code[i:i+4] != "=end":
                i += 1
            comments.append(code[comment_start:i].strip())
            i += 4


        else:
            i += 1

    return comments

