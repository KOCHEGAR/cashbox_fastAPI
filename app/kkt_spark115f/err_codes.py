# Prevent app from crash
FISCAL_ERROR_4 = 4  # Very dirty bugfix


def check_for_err_code(code):
    if code == _valid_codes:
        return False
    elif code == -1:
        return True
    else:
        return code in ERROR_CODES


_valid_codes = [0, -2, -3, FISCAL_ERROR_4]

ERROR_CODES = [
    1, 2, 3, 5, 6, 7, 9, 12, 16, 17, 20,
    21, 22, 26, 27, 28, 29, 34, 38, 40, 41, 42,
    43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54,
    55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 68, 69, 70,
    73, 74, 75, 76, 77, 78, 79, 81, 82, 83, 84, 85, 86, 87,
    89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101,
    103, 104, 105, 107, 108, 109, 111, 112, 117, 118, 119, 120,
    121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132,
    133, 138, 140, 141, 142, 143, 144, 145, 146, 147, 161, 162,
    163, 164, 165, 168, 169, 170, 171, 172, 173, 179, 180, 181,
    182, 183, 184, 185, 186, 187, 192, 197, 200, 201, 202, 203,
    207, 208, 210, 211, 212, 213, 214, 215, 219, 226, 227, 230,
    231, 232, 233, 235, 241, 247, 248, 250, 281, 282, 283, 284,
    285, 286, 287, 288, 289, 290, 291,
]