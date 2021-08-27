import re

text: str = "#天气 北京"
match_obj = re.match(r'^(#天气) ([\u4e00-\u9fa5]+)', text)

if match_obj:
    print("match_obj.group() : ", match_obj.group())
    print("match_obj.group(1) : ", match_obj.group(1))
    print("match_obj.group(2) : ", match_obj.group(2))
else:
    print("No match!!")
